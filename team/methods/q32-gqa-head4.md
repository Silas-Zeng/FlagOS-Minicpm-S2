# Q32 GQA head4 CTA拆分

把Q32长KV路径的CTA行块从BM256/w16改为BM128/w8，grid-y由2变4，尝试让CTA处理4个GQA query heads。四例数值门通过，但Q2018/KV14126组件ABBA中B慢28.7083%；保留负结果并停止，不进入服务。use_sme实际为3，和请求值229379不同。

- [20261030T002901364769Z-q32-head4-component](../runs/bi-v150/20261030T002901364769Z-q32-head4-component.md)：四例逐位与guard/readonly门通过；Q2018/KV14126组件A/B Event为7.983063/10.274864 ms，B慢28.7083%，停止，不进入服务/官方测量。
