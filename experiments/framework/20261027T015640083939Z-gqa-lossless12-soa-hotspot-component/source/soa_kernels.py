"""仅独立组件的BF16无损SoA writer/loader，非生产安装。"""
import triton
import triton.language as tl


@triton.jit
def _store_row(values,packed,metadata,page,group,slot):
    dims=tl.arange(0,128)
    pairs=tl.arange(0,64)
    bits=values.to(tl.uint16,bitcast=True)
    exp=((bits>>7)&255).to(tl.int32)
    base=tl.maximum(tl.max(exp,0)-15,0)
    compressed=tl.min(exp,0)>=base
    codes=tl.where(compressed,exp-base,exp&15)
    low=(((bits>>8)&128)|(bits&127)).to(tl.uint8)
    nibbles=(tl.gather(codes,pairs*2,0)|(tl.gather(codes,pairs*2+1,0)<<4)).to(tl.uint8)
    high=exp>>4
    high_nibbles=(tl.gather(high,pairs*2,0)|(tl.gather(high,pairs*2+1,0)<<4)).to(tl.uint8)
    data=packed+page.to(tl.int64)*16384+group*4096
    meta=metadata+page.to(tl.int64)*128+group*32+slot*2
    tl.store(data+slot*128+dims,low)
    tl.store(data+2048+slot*64+pairs,nibbles)
    tl.store(data+3072+slot*64+pairs,high_nibbles,mask=~compressed)
    tl.store(meta,tl.where(compressed,base,0).to(tl.uint8))
    tl.store(meta+1,compressed.to(tl.uint8))


@triton.jit
def encode_cache(source,packed,metadata):
    page=tl.program_id(0);group=tl.program_id(1);slot=tl.program_id(2)
    kind=group//2;head=group%2
    values=tl.load(source+page.to(tl.int64)*8192+kind*4096+slot*256+head*128+tl.arange(0,128))
    _store_row(values,packed,metadata,page,group,slot)


@triton.jit
def write_rows(key,value,slots,packed,metadata,INPUT_STRIDE:tl.constexpr):
    token=tl.program_id(0);head=tl.program_id(1);kind=tl.program_id(2)
    slot_id=tl.load(slots+token).to(tl.int64)
    if slot_id<0:return
    source=tl.where(kind==0,key,value)
    values=tl.load(source+token.to(tl.int64)*INPUT_STRIDE+head*128+tl.arange(0,128))
    _store_row(values,packed,metadata,slot_id//16,kind*2+head,slot_id%16)


@triton.jit
def load_bf16(packed,metadata,page,group,slot,dim,valid):
    data=packed+page.to(tl.int64)*16384+group*4096
    meta=metadata+page.to(tl.int64)*128+group*32+slot*2
    base=tl.load(meta,mask=valid,other=0).to(tl.uint16)
    mode=tl.load(meta+1,mask=valid,other=1)
    low=tl.load(data+slot*128+dim,mask=valid,other=0).to(tl.uint16)
    nib=tl.load(data+2048+slot*64+dim//2,mask=valid,other=0).to(tl.uint16)
    shift=(dim%2)*4
    code=(nib>>shift)&15
    high=tl.load(data+3072+slot*64+dim//2,mask=valid&(mode==0),other=0).to(tl.uint16)
    exp=tl.where(mode!=0,base+code,code|(((high>>shift)&15)<<4))
    bits=((low&128)<<8)|(low&127)|(exp<<7)
    return bits.to(tl.uint16).to(tl.bfloat16,bitcast=True)


@triton.jit
def decode_cache(packed,metadata,output):
    page=tl.program_id(0);group=tl.program_id(1);slot=tl.program_id(2)
    dims=tl.arange(0,128)
    values=load_bf16(packed,metadata,page,group,slot,dims,True)
    tl.store(output+page.to(tl.int64)*8192+(group//2)*4096+slot*256+(group%2)*128+dims,values)
