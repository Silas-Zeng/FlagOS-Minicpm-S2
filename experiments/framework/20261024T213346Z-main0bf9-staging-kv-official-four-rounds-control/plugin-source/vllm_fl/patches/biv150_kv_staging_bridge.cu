// 单层scratch、16KiB页的纯bit copy；不是模型算子或完成ACK。
#include <cuda_runtime.h>
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <type_traits>
#include <vector>

struct Layer { void* raw; void* host; std::size_t raw_bytes; std::size_t host_bytes; };
struct Submitted { std::size_t index_copies; std::size_t data_copies; std::size_t kernels; };
static_assert(sizeof(void*) == 8 && sizeof(std::size_t) == 8 && sizeof(Layer) == 32 && sizeof(Submitted) == 24, "64bit ABI");
static_assert(sizeof(uint4) == 16, "uint4必须恰16字节，完整16KiB页bit copy");
static_assert(std::is_pointer<cudaStream_t>::value && sizeof(cudaStream_t) == 8, "SDK stream ABI");
constexpr std::size_t PAGE = 16384;
constexpr std::size_t CAP = std::size_t(1) << 30;

extern "C" std::uint32_t staging_abi() { return 1; }
extern "C" std::size_t staging_layer_size() { return sizeof(Layer); }
extern "C" std::size_t staging_submitted_size() { return sizeof(Submitted); }

template<bool GATHER>
__global__ void pages_bitcopy(uint4* raw, uint4* scratch, const std::int64_t* ids) {
    const std::size_t logical = static_cast<std::size_t>(blockIdx.x);
    const std::size_t physical = static_cast<std::size_t>(ids[logical]);
    constexpr std::size_t WORDS = PAGE / sizeof(uint4);
    for (std::size_t i = threadIdx.x; i < WORDS; i += blockDim.x) {
        if (GATHER) scratch[logical * WORDS + i] = raw[physical * WORDS + i];
        else raw[physical * WORDS + i] = scratch[logical * WORDS + i];
    }
}

static bool span(const void* p, std::size_t bytes, std::size_t alignment) {
    const auto x = reinterpret_cast<std::uintptr_t>(p);
    return p && bytes && x % alignment == 0 && x <= std::numeric_limits<std::uintptr_t>::max() - bytes;
}
static bool overlaps(const void* a, std::size_t an, const void* b, std::size_t bn) {
    const auto x = reinterpret_cast<std::uintptr_t>(a), y = reinterpret_cast<std::uintptr_t>(b);
    return x < y + bn && y < x + an;
}

// CPU ids须pinned，device ids和scratch必须独立、同cuda0；调用者验证真实Tensor。
// 全部几何/页号/跨层区间先验后才入队。任意失败不重试，必须由调用者settle。
extern "C" int staging_submit(const Layer* layers, std::size_t layer_count,
    const std::int64_t* host_ids, std::int64_t* device_ids, std::size_t page_count,
    std::size_t pool_blocks, void* scratch, std::size_t scratch_bytes,
    std::uint32_t direction, void* stream, Submitted* submitted) {
    if (!submitted) return -1001;
    *submitted = {0, 0, 0};
    if (!layers || (layer_count != 1 && layer_count != 42) || !page_count ||
        page_count > CAP / PAGE / layer_count || !pool_blocks ||
        pool_blocks > std::numeric_limits<std::size_t>::max() / PAGE ||
        page_count > pool_blocks || (direction != 1 && direction != 2)) return -1001;
    const std::size_t raw_bytes = pool_blocks * PAGE, payload = page_count * PAGE, index_bytes = page_count * 8;
    if (scratch_bytes != payload || !span(scratch, payload, 16) ||
        !span(host_ids, index_bytes, 8) || !span(device_ids, index_bytes, 8) ||
        overlaps(scratch, payload, host_ids, index_bytes) || overlaps(scratch, payload, device_ids, index_bytes) ||
        overlaps(host_ids, index_bytes, device_ids, index_bytes)) return -1002;
    for (std::size_t i = 0; i < layer_count; ++i) {
        const auto& d = layers[i];
        if (d.raw_bytes != raw_bytes || d.host_bytes != payload ||
            !span(d.raw, raw_bytes, 16) || !span(d.host, payload, 16) ||
            overlaps(d.raw, raw_bytes, d.host, payload) || overlaps(d.raw, raw_bytes, scratch, payload) ||
            overlaps(d.host, payload, scratch, payload) || overlaps(d.raw, raw_bytes, device_ids, index_bytes) ||
            overlaps(d.host, payload, host_ids, index_bytes) || overlaps(d.raw, raw_bytes, host_ids, index_bytes) ||
            overlaps(d.host, payload, device_ids, index_bytes)) return -1002;
        for (std::size_t j = 0; j < i; ++j) {
            const auto& p = layers[j];
            if (overlaps(d.raw, raw_bytes, p.raw, raw_bytes) || overlaps(d.host, payload, p.host, payload) ||
                overlaps(d.raw, raw_bytes, p.host, payload) || overlaps(d.host, payload, p.raw, raw_bytes)) return -1002;
        }
    }
    // 仅CPU复制元数据验证唯一性，不排序实际上传页序。
    try {
        std::vector<std::int64_t> ordered(host_ids, host_ids + page_count);
        for (const auto id : ordered) if (id < 0 || static_cast<std::size_t>(id) >= pool_blocks) return -1003;
        std::sort(ordered.begin(), ordered.end());
        if (std::adjacent_find(ordered.begin(), ordered.end()) != ordered.end()) return -1003;
    } catch (...) { return -1007; }
    int device = -1;
    auto code = cudaGetDevice(&device);
    if (code != cudaSuccess) return static_cast<int>(code);
    if (device != 0) return -1004;
    code = cudaPeekAtLastError();
    if (code != cudaSuccess) return static_cast<int>(code);
    const auto sdk_stream = reinterpret_cast<cudaStream_t>(stream);
    code = cudaMemcpyAsync(device_ids, host_ids, index_bytes, cudaMemcpyHostToDevice, sdk_stream);
    if (code != cudaSuccess) return static_cast<int>(code);
    ++submitted->index_copies;
    for (std::size_t layer = 0; layer < layer_count; ++layer) {
        const auto& d = layers[layer];
        if (direction == 1) {
            pages_bitcopy<true><<<static_cast<unsigned>(page_count), 256, 0, sdk_stream>>>(
                static_cast<uint4*>(d.raw), static_cast<uint4*>(scratch), device_ids);
            code = cudaGetLastError();
            if (code != cudaSuccess) return static_cast<int>(code);
            ++submitted->kernels;
            code = cudaMemcpyAsync(d.host, scratch, payload, cudaMemcpyDeviceToHost, sdk_stream);
            if (code != cudaSuccess) return static_cast<int>(code);
            ++submitted->data_copies;
        } else {
            code = cudaMemcpyAsync(scratch, d.host, payload, cudaMemcpyHostToDevice, sdk_stream);
            if (code != cudaSuccess) return static_cast<int>(code);
            ++submitted->data_copies;
            pages_bitcopy<false><<<static_cast<unsigned>(page_count), 256, 0, sdk_stream>>>(
                static_cast<uint4*>(d.raw), static_cast<uint4*>(scratch), device_ids);
            code = cudaGetLastError();
            if (code != cudaSuccess) return static_cast<int>(code);
            ++submitted->kernels;
        }
    }
    return 0; // 只是提交；scratch/IDs/host/raw必须强持到同stream真event或failure settle。
}
