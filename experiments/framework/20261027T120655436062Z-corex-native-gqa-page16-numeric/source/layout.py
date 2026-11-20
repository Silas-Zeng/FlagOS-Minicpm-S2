"""独立CPU索引参考；没有device builtin或Attention近似实现。"""
def k_index(slot,dim):
 r=dim%32;c=slot;pair=r//2
 return (dim//32)*512+(c//4)*128+(pair&3)*32+((pair//8)^(c//8))*16+(((pair//4)&1)^((c//4)&1))*8+(c&3)*2+(r&1)
def v_index(slot,dim):
 i,c=divmod(dim,16);r=slot//2
 return i*256+(r//4)*128+((r*32+c*2+(slot&1)+i*64)&127)
def expected_shared(cache_bits,page,np):
 out=np.empty((2,4096),dtype=np.uint16)
 for head in range(2):
  for slot in range(16):
   for dim in range(128):
    out[head,k_index(slot,dim)]=cache_bits[page,0,slot,head,dim]
    out[head,2048+v_index(slot,dim)]=cache_bits[page,1,slot,head,dim]
 return out

def check_symbolic():
 # Original production Q-stage stores, independent of the new direct-load code.
 stage={}
 for lane in range(64):
  base=(384 if lane&8 else 0)|((lane&48)<<5)|((lane&7)<<3)
  for headpair,byte in ((0,base),(2,base+64),(4,base^128),(6,(base^128)+64)):
   values=((headpair,2*lane),(headpair+1,2*lane),(headpair,2*lane+1),(headpair+1,2*lane+1))
   for i,value in enumerate(values):
    assert byte//2+i not in stage;stage[byte//2+i]=value
 assert set(stage)==set(range(1024))
 for lane in range(64):
  for k in range(8):
   byte=((lane*4)^(384 if k&1 else 0))+(k//2)*512
   actual=(stage[byte//2],stage[byte//2+1])
   assert actual==((2*(lane//16),16*k+lane%16),(2*(lane//16)+1,16*k+lane%16))
 assert {k_index(s,d) for s in range(16) for d in range(128)}==set(range(2048))
 assert {v_index(s,d) for s in range(16) for d in range(128)}==set(range(2048))
 # Symbolic original P shuffle matches the native A fragment's row pair.
 p0=[(lane//16,lane%16) for lane in range(64)]
 p1=[(lane//16+4,lane%16) for lane in range(64)]
 a=[p1[i] if i&16 else p0[i] for i in range(64)]
 b=[p0[i] if i&16 else p1[i] for i in range(64)]
 for lane in range(64):
  index=((lane&16)<<1)|((lane&32)>>1)|(lane&15)
  u,v=a[index],b[index^16]
  pair=(v,u) if lane&32 else (u,v)
  assert pair==((2*(lane//16),lane%16),(2*(lane//16)+1,lane%16))
 return dict(original_Q_store_load_inverse=True,Q_native_fragments=512,Q_packed_words=1024,K_shared_bijection_2048=True,V_shared_bijection_2048=True,original_P_shuffle_equals_native_row_pair=True)
