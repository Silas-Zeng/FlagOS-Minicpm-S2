; ModuleID = 'LLVMDialectModule'
source_filename = "LLVMDialectModule"
target datalayout = "e-p:64:64-p1:64:64-p2:32:32-p3:32:32-p4:64:64-p5:32:32-p6:32:32-i64:64-v16:16-v24:32-v32:32-v48:64-v96:128-v192:256-v256:256-v512:512-v1024:1024-v2048:2048-n32:64-S32-A5"
target triple = "bi-iluvatar-ilurt"

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(none)
declare !dbg !4 float @llvm.nvvm.ex2.approx.ftz.f32(float) #0

; Function Attrs: nounwind
define iluvatar_kernel void @probability_reference(ptr addrspace(1) %0, ptr addrspace(1) %1, ptr addrspace(1) %2, ptr addrspace(1) readnone captures(none) %3, ptr addrspace(1) readnone captures(none) %4) local_unnamed_addr #1 !dbg !7 {
  %6 = tail call i32 @llvm.nvvm.read.ptx.sreg.ctaid.x(), !dbg !8
  %7 = tail call i32 @llvm.nvvm.read.ptx.sreg.tid.x(), !dbg !9
  %8 = and i32 %7, 63, !dbg !9
  %9 = and i32 %7, 15, !dbg !9
  %10 = shl i32 %6, 4, !dbg !10
  %11 = sext i32 %10 to i64, !dbg !11
  %12 = getelementptr float, ptr addrspace(1) %0, i64 %11, !dbg !11
  %13 = zext nneg i32 %9 to i64, !dbg !12
  %14 = getelementptr float, ptr addrspace(1) %12, i64 %13, !dbg !12
  %15 = tail call <1 x float> @llvm.bi.load.kop.v1f32(ptr addrspace(1) %14, i32 0, i1 false), !dbg !13
  %16 = extractelement <1 x float> %15, i64 0, !dbg !13
  %17 = bitcast float %16 to i32, !dbg !14
  %18 = xor i32 %8, 8, !dbg !14
  %19 = tail call i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %17, i32 %18), !dbg !14
  %20 = bitcast i32 %19 to float, !dbg !14
  %21 = tail call float @llvm.maxnum.f32(float %16, float %20), !dbg !19
  %22 = bitcast float %21 to i32, !dbg !14
  %23 = xor i32 %8, 4, !dbg !14
  %24 = tail call i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %22, i32 %23), !dbg !14
  %25 = bitcast i32 %24 to float, !dbg !14
  %26 = tail call float @llvm.maxnum.f32(float %21, float %25), !dbg !19
  %27 = bitcast float %26 to i32, !dbg !14
  %28 = xor i32 %8, 2, !dbg !14
  %29 = tail call i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %27, i32 %28), !dbg !14
  %30 = bitcast i32 %29 to float, !dbg !14
  %31 = tail call float @llvm.maxnum.f32(float %26, float %30), !dbg !19
  %32 = bitcast float %31 to i32, !dbg !14
  %33 = xor i32 %8, 1, !dbg !14
  %34 = tail call i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %32, i32 %33), !dbg !14
  %35 = bitcast i32 %34 to float, !dbg !14
  %36 = tail call float @llvm.maxnum.f32(float %31, float %35), !dbg !19
  %37 = fsub float %16, %36, !dbg !20
  %38 = tail call float @llvm.nvvm.ex2.approx.ftz.f32(float %37), !dbg !21
  %39 = getelementptr float, ptr addrspace(1) %1, i64 %11, !dbg !22
  %40 = getelementptr float, ptr addrspace(1) %39, i64 %13, !dbg !23
  %41 = ptrtoint ptr addrspace(1) %40 to i64, !dbg !24
  %extelt.offset = lshr i64 %41, 32, !dbg !24
  %42 = trunc nuw i64 %extelt.offset to i32, !dbg !24
  %43 = trunc i64 %41 to i32, !dbg !24
  %44 = tail call i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %43, i32 0), !dbg !24
  %45 = tail call i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %42, i32 0), !dbg !24
  %46 = insertelement <2 x i32> poison, i32 %44, i64 0, !dbg !24
  %47 = insertelement <2 x i32> %46, i32 %45, i64 1, !dbg !24
  %48 = bitcast <2 x i32> %47 to i64, !dbg !24
  %49 = inttoptr i64 %48 to ptr addrspace(1), !dbg !24
  %50 = and i32 %7, 48, !dbg !24
  %51 = icmp eq i32 %50, 0, !dbg !24
  %52 = bitcast float %38 to i32, !dbg !24
  %53 = tail call i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 0, i32 0), !dbg !24
  %54 = sub i64 %41, %48, !dbg !24
  %55 = trunc i64 %54 to i32, !dbg !24
  tail call void @llvm.bi.stp.vs.pred.i32(i32 %52, ptr addrspace(1) %49, i32 %53, i32 %55, i32 0, i1 %51), !dbg !24
  %56 = getelementptr bfloat, ptr addrspace(1) %2, i64 %11, !dbg !25
  %57 = getelementptr bfloat, ptr addrspace(1) %56, i64 %13, !dbg !26
  %58 = fptrunc float %38 to bfloat, !dbg !27
  %59 = ptrtoint ptr addrspace(1) %57 to i64, !dbg !28
  %extelt.offset1 = lshr i64 %59, 32, !dbg !28
  %60 = trunc nuw i64 %extelt.offset1 to i32, !dbg !28
  %61 = trunc i64 %59 to i32, !dbg !28
  %62 = tail call i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %61, i32 0), !dbg !28
  %63 = tail call i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %60, i32 0), !dbg !28
  %64 = insertelement <2 x i32> poison, i32 %62, i64 0, !dbg !28
  %65 = insertelement <2 x i32> %64, i32 %63, i64 1, !dbg !28
  %66 = bitcast <2 x i32> %65 to i64, !dbg !28
  %67 = inttoptr i64 %66 to ptr addrspace(1), !dbg !28
  %68 = bitcast bfloat %58 to i16, !dbg !28
  %69 = sub i64 %59, %66, !dbg !28
  %70 = trunc i64 %69 to i32, !dbg !28
  tail call void @llvm.bi.stp.vs.pred.i16(i16 %68, ptr addrspace(1) %67, i32 %53, i32 %70, i32 0, i1 %51), !dbg !28
  ret void, !dbg !29
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef range(i32 0, 2147483647) i32 @llvm.nvvm.read.ptx.sreg.ctaid.x() #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef range(i32 0, 4096) i32 @llvm.nvvm.read.ptx.sreg.tid.x() #2

; Function Attrs: nounwind
declare <1 x float> @llvm.bi.load.kop.v1f32(ptr addrspace(1), i32 immarg, i1 immarg) #3

; Function Attrs: convergent nofree nounwind memory(none)
declare i32 @llvm.bi.slb.shfl.idx.b32.i32(i32, i32) #4

; Function Attrs: mustprogress nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #5

; Function Attrs: nounwind memory(argmem: write)
declare void @llvm.bi.stp.vs.pred.i32(i32, ptr addrspace(1) writeonly, i32, i32, i32 immarg, i1) #6

; Function Attrs: nounwind memory(argmem: write)
declare void @llvm.bi.stp.vs.pred.i16(i16, ptr addrspace(1) writeonly, i32, i32, i32 immarg, i1) #6

attributes #0 = { mustprogress nocallback nofree nosync nounwind willreturn memory(none) }
attributes #1 = { nounwind "nvvm.reqntid"="32" }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { nounwind }
attributes #4 = { convergent nofree nounwind memory(none) }
attributes #5 = { mustprogress nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nounwind memory(argmem: write) }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3}

!0 = distinct !DICompileUnit(language: DW_LANG_C, file: !1, producer: "triton", isOptimized: true, runtimeVersion: 0, emissionKind: LineTablesOnly)
!1 = !DIFile(filename: "exp2_reference.py", directory: "/workspace/experiments/minicpm-s2/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/source")
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 4, !"nvvm-reflect-ftz", i32 1}
!4 = !DISubprogram(name: "llvm.nvvm.ex2.approx.ftz.f32", linkageName: "llvm.nvvm.ex2.approx.ftz.f32", scope: !1, file: !1, line: 10, type: !5, scopeLine: 10, spFlags: DISPFlagOptimized)
!5 = !DISubroutineType(cc: DW_CC_normal, types: !6)
!6 = !{}
!7 = distinct !DISubprogram(name: "probability_reference", linkageName: "probability_reference", scope: !1, file: !1, line: 6, type: !5, scopeLine: 6, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!8 = !DILocation(line: 7, column: 22, scope: !7)
!9 = !DILocation(line: 8, column: 23, scope: !7)
!10 = !DILocation(line: 9, column: 24, scope: !7)
!11 = !DILocation(line: 9, column: 20, scope: !7)
!12 = !DILocation(line: 9, column: 27, scope: !7)
!13 = !DILocation(line: 9, column: 14, scope: !7)
!14 = !DILocation(line: 213, column: 40, scope: !15, inlinedAt: !17)
!15 = distinct !DILexicalBlockFile(scope: !7, file: !16, discriminator: 0)
!16 = !DIFile(filename: "standard.py", directory: "/usr/local/lib/python3.12/site-packages/triton/language")
!17 = !DILocation(line: 10, column: 25, scope: !18)
!18 = distinct !DILexicalBlockFile(scope: !7, file: !1, discriminator: 0)
!19 = !DILocation(line: 192, column: 27, scope: !15, inlinedAt: !14)
!20 = !DILocation(line: 10, column: 16, scope: !7)
!21 = !DILocation(line: 10, column: 14, scope: !7)
!22 = !DILocation(line: 11, column: 25, scope: !7)
!23 = !DILocation(line: 11, column: 32, scope: !7)
!24 = !DILocation(line: 11, column: 39, scope: !7)
!25 = !DILocation(line: 12, column: 19, scope: !7)
!26 = !DILocation(line: 12, column: 26, scope: !7)
!27 = !DILocation(line: 12, column: 38, scope: !7)
!28 = !DILocation(line: 12, column: 33, scope: !7)
!29 = !DILocation(line: 12, column: 4, scope: !7)
