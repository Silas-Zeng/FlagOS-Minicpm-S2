"""组件冷门的CPU metadata合同；不在Graph计时内伪装生产准入成本。"""
def validate(lengths,table,slots,page_size=16):
    if page_size!=16 or len(lengths)!=len(table) or len(slots)!=len(lengths):
        raise ValueError('只接受相同B的page16元数据')
    writes=[]
    for row,(length,slot) in enumerate(zip(lengths,slots)):
        if length<0 or length>len(table[row])*16:raise ValueError('长度越界')
        if length==0:
            if slot>=0:raise ValueError('L0不能携有效append')
            continue
        if slot<0:continue
        if slot!=int(table[row][(length-1)//16])*16+(length-1)%16:
            raise ValueError('append不对应seq_len-1')
        writes.append((row,slot))
    for row,slot in writes:
        block,offset=divmod(slot,16)
        for other,length in enumerate(lengths):
            for col in range((length+15)//16):
                logical_position=col*16+offset
                if (int(table[other][col])==block and logical_position<length
                        and not (other==row and logical_position==length-1)):
                    raise ValueError('append同/跨请求非尾可见alias，拒绝融合')
    return dict(valid=True,positive_writes=len(writes),admission='显式CPU数据；非生产每步证明或免费元数据路径')
