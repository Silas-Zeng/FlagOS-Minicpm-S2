// 只读硬件属性；唯一设备owner串行运行。无模型、分配、kernel、同步或配置设置。
// g++ -std=c++17 -O2 -I/usr/local/corex-4.5.0/include query_biv150_resources.cpp -ldl -o query_biv150_resources
#include <IX/ixrt/ix.h>
#include <dlfcn.h>
#include <iostream>
#include <string>
#include <vector>
static std::string quoted(const std::string &s) {
    std::string r(1,char(34));
    for(unsigned char c:s) {
        if(c==34||c==92) r+=char(92);
        r+=c<32?'?':char(c);
    }
    return r+char(34);
}
static std::string key(const char *name) { return quoted(name)+":"; }
static int failed(const char *status) {
    std::cout<<'{'<<key("status")<<quoted(status)<<'}'<<std::endl;return 2;
}
struct Row { const char *name; int enumeration,rc,value; };
int main(int argc,char**) {
    if(argc!=1) return failed("no_arguments_allowed");
    void *library=dlopen("libcuda.so.1",RTLD_NOW|RTLD_LOCAL);
    if(!library) return failed("library_unavailable");
    auto init=reinterpret_cast<decltype(&ixdrvInit)>(dlsym(library,"ixdrvInit"));
    auto get_count=reinterpret_cast<decltype(&ixdrvDeviceGetCount)>(dlsym(library,"ixdrvDeviceGetCount"));
    auto get_device=reinterpret_cast<decltype(&ixdrvDeviceGet)>(dlsym(library,"ixdrvDeviceGet"));
    auto get_name=reinterpret_cast<decltype(&ixdrvDeviceGetName)>(dlsym(library,"ixdrvDeviceGetName"));
    auto attribute=reinterpret_cast<decltype(&ixdrvDeviceGetAttribute)>(dlsym(library,"ixdrvDeviceGetAttribute"));
    auto total_mem=reinterpret_cast<decltype(&ixdrvDeviceTotalMem)>(dlsym(library,"ixdrvDeviceTotalMem_v2"));
    auto ctx_state=reinterpret_cast<decltype(&ixdrvDevicePrimaryCtxGetState)>(dlsym(library,"ixdrvDevicePrimaryCtxGetState"));
    if(!init||!get_count||!get_device||!get_name||!attribute) return failed("required_actual_ixdrv_symbol_missing");
    Dl_info info{};dladdr(reinterpret_cast<void*>(init),&info);
    int init_rc=int(init(0));int count=-1;int count_rc=init_rc?init_rc:int(get_count(&count));
    IXDRVdevice device{};int device_rc=count_rc?count_rc:(count==1?int(get_device(&device,0)):-9998);
    std::cout<<'{'<<key("kind")<<quoted("read_only_no_kernel_no_allocation_no_settings")
             <<','<<key("loaded_driver")<<quoted(info.dli_fname?info.dli_fname:"")
             <<','<<key("init_return_code")<<init_rc<<','<<key("device_count_return_code")<<count_rc
             <<','<<key("device_count")<<count<<','<<key("device_get_return_code")<<device_rc;
    if(device_rc) { std::cout<<','<<key("status")<<quoted("device_not_single_or_unavailable")<<'}'<<std::endl;return 2; }
    unsigned int flags_before=0,flags_after=0;int active_before=-1,active_after=-1;
    int ctx_before_rc=ctx_state?int(ctx_state(device,&flags_before,&active_before)):-9999;
    char name[256]{};int name_rc=int(get_name(name,sizeof(name),device));
    size_t bytes=0;int bytes_rc=total_mem?int(total_mem(&bytes,device)):-9999;
    std::vector<Row> rows;
    auto query=[&](const char *name,IXDRVdevice_attribute field) {
        int value=0;int rc=int(attribute(&value,field,device));rows.push_back({name,int(field),rc,value});
    };
#define READ(field) query(#field,field)
    READ(IXDRV_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT);
    READ(IXDRV_DEVICE_ATTRIBUTE_WARP_SIZE);
    READ(IXDRV_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_MULTIPROCESSOR);
    READ(IXDRV_DEVICE_ATTRIBUTE_MAX_REGISTERS_PER_MULTIPROCESSOR);
    READ(IXDRV_DEVICE_ATTRIBUTE_MAX_THREADS_PER_MULTIPROCESSOR);
    READ(IXDRV_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK);
    READ(IXDRV_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK);
    READ(IXDRV_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN);
    READ(IXDRV_DEVICE_ATTRIBUTE_MAX_REGISTERS_PER_BLOCK);
    READ(IXDRV_DEVICE_ATTRIBUTE_L2_CACHE_SIZE);
    READ(IXDRV_DEVICE_ATTRIBUTE_GLOBAL_L1_CACHE_SUPPORTED);
    READ(IXDRV_DEVICE_ATTRIBUTE_LOCAL_L1_CACHE_SUPPORTED);
    READ(IXDRV_DEVICE_ATTRIBUTE_ASYNC_ENGINE_COUNT);
    READ(IXDRV_DEVICE_ATTRIBUTE_CONCURRENT_KERNELS);
    READ(IXDRV_DEVICE_ATTRIBUTE_CLOCK_RATE);
    READ(IXDRV_DEVICE_ATTRIBUTE_MEMORY_CLOCK_RATE);
    READ(IXDRV_DEVICE_ATTRIBUTE_GLOBAL_MEMORY_BUS_WIDTH);
    READ(IXDRV_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR);
    READ(IXDRV_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR);
#undef READ
    int ctx_after_rc=ctx_state?int(ctx_state(device,&flags_after,&active_after)):-9999;
    std::cout<<','<<key("device_name_return_code")<<name_rc<<','<<key("device_name")<<quoted(name)
             <<','<<key("total_memory_return_code")<<bytes_rc<<','<<key("total_memory_bytes");
    if(bytes_rc) std::cout<<"null";else std::cout<<bytes;
    std::cout<<','<<key("primary_context_before")<<'{'<<key("return_code")<<ctx_before_rc<<','<<key("flags")<<flags_before<<','<<key("active")<<active_before<<'}'
             <<','<<key("primary_context_after")<<'{'<<key("return_code")<<ctx_after_rc<<','<<key("flags")<<flags_after<<','<<key("active")<<active_after<<'}'
             <<','<<key("attributes")<<'[';
    bool partial=false;
    for(size_t i=0;i<rows.size();++i) {
        const auto &r=rows[i];if(i)std::cout<<',';
        std::cout<<'{'<<key("enum_name")<<quoted(r.name)<<','<<key("enum_value_from_actual_sdk")<<r.enumeration
                 <<','<<key("return_code")<<r.rc<<','<<key("value");
        if(r.rc) {std::cout<<"null";partial=true;} else std::cout<<r.value;
        std::cout<<'}';
    }
    std::cout<<']'<<','<<key("max_blocks_per_multiprocessor")<<quoted("unobserved_no_enum_in_actual_ix_h")
             <<','<<key("kernel_properties")<<quoted("unobserved_requires_live_CUfunction_in_own_process")
             <<','<<key("status")<<quoted(partial?"read_complete_some_attributes_unsupported":"read_complete")<<'}'<<std::endl;
    // No PrimaryCtxRetain, context creation, stream, allocation, sync or Set API.
    // Hold library for the process lifetime; never close a live external handle.
    return 0;
}
