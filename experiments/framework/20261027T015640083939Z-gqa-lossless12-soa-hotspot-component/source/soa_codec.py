"""page内SoA无损BF16位协议的CPU参考；不依赖Torch。"""
import numpy as np

PAGE_BYTES=16384
META_BYTES=128


def store_row(data,metadata,page,kind,head,slot,bits):
    bits=np.asarray(bits)
    assert bits.dtype==np.uint16 and bits.shape==(128,)
    exp=((bits>>7)&255).astype(np.uint16)
    base=max(0,int(exp.max())-15)
    compressed=bool(int(exp.min())>=base)
    codes=exp-base if compressed else exp&15
    group=kind*2+head
    low=(((bits>>8)&128)|(bits&127)).astype(np.uint8)
    data[page,group,slot*128:slot*128+128]=low
    data[page,group,2048+slot*64:2048+(slot+1)*64]=(codes[0::2]|(codes[1::2]<<4)).astype(np.uint8)
    if not compressed:
        high=(exp>>4).astype(np.uint8)
        data[page,group,3072+slot*64:3072+(slot+1)*64]=high[0::2]|(high[1::2]<<4)
    metadata[page,group,slot*2:slot*2+2]=(base if compressed else 0,int(compressed))


def encode(bits):
    assert bits.dtype==np.uint16 and bits.ndim==5 and bits.shape[1:]==(2,16,2,128)
    data=np.full((len(bits),4,4096),165,dtype=np.uint8)
    metadata=np.full((len(bits),4,32),204,dtype=np.uint8)
    for p in range(len(bits)):
        for kind in range(2):
            for head in range(2):
                for slot in range(16):store_row(data,metadata,p,kind,head,slot,bits[p,kind,slot,head])
    return data,metadata


def decode(data,metadata):
    out=np.empty((len(data),2,16,2,128),dtype=np.uint16)
    for p in range(len(data)):
        for kind in range(2):
            for head in range(2):
                group=kind*2+head
                for slot in range(16):
                    low=data[p,group,slot*128:(slot+1)*128].astype(np.uint16)
                    n=data[p,group,2048+slot*64:2048+(slot+1)*64]
                    codes=np.empty(128,dtype=np.uint16);codes[0::2]=n&15;codes[1::2]=n>>4
                    base,mode=map(int,metadata[p,group,slot*2:slot*2+2])
                    if mode:exp=codes+base
                    else:
                        n=data[p,group,3072+slot*64:3072+(slot+1)*64]
                        hi=np.empty(128,dtype=np.uint16);hi[0::2]=n&15;hi[1::2]=n>>4
                        exp=codes|(hi<<4)
                    out[p,kind,slot,head]=((low&128)<<8)|(low&127)|(exp<<7)
    return out


def real_stats(k,v):
    result={}
    for label,bits in (('K',k),('V',v)):
        assert bits.dtype==np.uint16 and bits.ndim==4 and bits.shape[1:]==(128,2,128)
        exp=((bits>>7)&255).astype(np.int32)
        raw=(exp.max(-1)-exp.min(-1))>15
        # 每层、head、16slot页；sample是连续128prompt位置，真实slot另核。
        groups=raw.transpose(0,2,1).reshape(-1,16)
        pairs=groups.reshape(-1,8,2).any(-1)
        actual={}
        for sector in (32,64,128):
            high=int(raw.sum())*64 if sector<=64 else int(pairs.sum())*128
            total=bits.size*2
            traffic=int(raw.size*192+raw.size*2+high)
            actual[str(sector)]=dict(modeled_bytes=traffic,fraction_saved=1-traffic/total,
                assumption='page/head内各plane连续且按粒度对齐；metadata按2B/row摊销，不是实测事务')
        result[label]=dict(rows=int(raw.size),raw_fallback_rows=int(raw.sum()),
            raw_row_fraction=float(raw.mean()),tail_128B_pairs=int(pairs.sum()),
            modeled_sector_traffic=actual)
    return result
