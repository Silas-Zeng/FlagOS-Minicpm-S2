// 独立Event短门：直接SDK事件，绕过Torch事件缓存；不创建流或全设备同步。
#include <cuda_runtime_api.h>
#include <cstddef>
#include <cstdint>
#include <type_traits>

static_assert(sizeof(void*) == 8, "只接受已核64位Corex ABI");
static_assert(std::is_pointer<cudaEvent_t>::value, "SDK event须为真实指针类型");
static_assert(std::is_pointer<cudaStream_t>::value, "SDK stream须为真实指针类型");
static_assert(sizeof(cudaEvent_t) == sizeof(void*), "event ABI不符");
static_assert(sizeof(cudaStream_t) == sizeof(void*), "stream ABI不符");

extern "C" {

std::uint32_t biv150_event_bridge_abi() noexcept { return 1; }

std::uint32_t biv150_event_creation_flags() noexcept {
  return cudaEventBlockingSync | cudaEventDisableTiming;
}

int biv150_event_create(void** output) noexcept {
  if (!output) return -1001;
  *output = nullptr;
  cudaEvent_t event = nullptr;
  const auto status = cudaEventCreateWithFlags(
      &event, cudaEventBlockingSync | cudaEventDisableTiming);
  // 即使SDK失败却给了handle，也交回owner清理；不能遗失部分构造资源。
  *output = reinterpret_cast<void*>(event);
  if (status != cudaSuccess) return static_cast<int>(status);
  return event ? 0 : -1002;
}

int biv150_event_record(void* handle, void* stream) noexcept {
  if (!handle) return -1001;
  // stream是调用者提供的实际当前流；合法default handle0也不另换流。
  return static_cast<int>(cudaEventRecord(
      reinterpret_cast<cudaEvent_t>(handle), reinterpret_cast<cudaStream_t>(stream)));
}

int biv150_event_query(void* handle, int* ready) noexcept {
  if (!handle || !ready) return -1001;
  *ready = 0;
  const auto status = cudaEventQuery(reinterpret_cast<cudaEvent_t>(handle));
  if (status == cudaSuccess) {
    *ready = 1;
    return 0;
  }
  if (status == cudaErrorNotReady) return 0;
  return static_cast<int>(status);  // 不清错/不把其它错误当未完成。
}

int biv150_event_synchronize(void* handle) noexcept {
  if (!handle) return -1001;
  return static_cast<int>(cudaEventSynchronize(reinterpret_cast<cudaEvent_t>(handle)));
}

int biv150_event_destroy(void* handle) noexcept {
  if (!handle) return -1001;
  return static_cast<int>(cudaEventDestroy(reinterpret_cast<cudaEvent_t>(handle)));
}

}  // extern "C"
