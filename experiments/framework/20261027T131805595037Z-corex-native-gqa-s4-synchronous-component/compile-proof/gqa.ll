; ModuleID = '/workspace/experiments/minicpm-s2/scripts/corex-native-gqa-s4-compile-1cf7105d/gqa_s4_draft.cu'
source_filename = "/workspace/experiments/minicpm-s2/scripts/corex-native-gqa-s4-compile-1cf7105d/gqa_s4_draft.cu"
target datalayout = "e-p:64:64-p1:64:64-p2:32:32-p3:32:32-p4:64:64-p5:32:32-p6:32:32-i64:64-v16:16-v24:32-v32:32-v48:64-v96:128-v192:256-v256:256-v512:512-v1024:1024-v2048:2048-n32:64-S32-A5"
target triple = "bi-iluvatar-ilurt"

%struct.__ix_bfloat16 = type { i16 }

$_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_ = comdat any

$_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage = comdat any

@gSyncThreadsFlag = dso_local local_unnamed_addr addrspace(3) global i32 undef, align 4
@_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage = linkonce_odr dso_local addrspace(3) global [2048 x i32] undef, comdat, align 16
@gPrintBuf = weak dso_local addrspace(1) externally_initialized global ptr null, align 8
@gAssertReason = weak dso_local addrspace(1) externally_initialized global ptr null, align 8
@llvm.compiler.used = appending global [2 x ptr] [ptr addrspacecast (ptr addrspace(1) @gAssertReason to ptr), ptr addrspacecast (ptr addrspace(1) @gPrintBuf to ptr)], section "llvm.metadata"

; Function Attrs: convergent mustprogress norecurse nounwind
define dso_local iluvatar_kernel void @_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_(ptr addrspace(1) noundef readonly captures(none) %0, ptr addrspace(1) noundef %1, ptr addrspace(1) noundef %2, ptr addrspace(1) noundef readonly captures(none) %3, ptr addrspace(1) noundef readonly captures(none) %4, float noundef %5, i64 noundef %6, i64 noundef %7, i64 noundef %8, i64 noundef %9, i64 noundef %10, i64 noundef %11, i64 noundef %12, i64 noundef %13, ptr addrspace(1) noundef writeonly captures(none) %14, ptr addrspace(1) noundef writeonly captures(none) %15, ptr addrspace(1) noundef writeonly captures(none) %16) local_unnamed_addr #0 comdat {
  %18 = tail call i32 @llvm.bi.lane.id(), !range !4, !noundef !5
  %19 = tail call noundef i32 @llvm.nvvm.read.ptx.sreg.ctaid.x(), !range !6
  %20 = tail call noundef i32 @llvm.nvvm.read.ptx.sreg.ctaid.y(), !range !7
  %21 = tail call noundef i32 @llvm.nvvm.read.ptx.sreg.ctaid.z(), !range !7
  %22 = lshr i32 %18, 4
  %23 = and i32 %18, 15
  %24 = zext nneg i32 %19 to i64
  %25 = getelementptr inbounds nuw i32, ptr addrspace(1) %3, i64 %24
  %26 = load i32, ptr addrspace(1) %25, align 4
  %27 = add i32 %26, 63
  %28 = lshr i32 %27, 6
  %29 = mul i32 %28, %21
  %30 = shl i32 %29, 4
  %31 = icmp slt i32 %30, %26
  br i1 %31, label %32, label %1061

32:                                               ; preds = %17
  %33 = mul nsw i64 %7, %24
  %34 = getelementptr inbounds %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %33
  %35 = shl nuw nsw i32 %20, 3
  %36 = shl nuw nsw i32 %22, 1
  %37 = or disjoint i32 %36, %35
  %38 = zext nneg i32 %37 to i64
  %39 = mul nsw i64 %8, %38
  %40 = zext nneg i32 %23 to i64
  %41 = getelementptr %struct.__ix_bfloat16, ptr addrspace(1) %34, i64 %39
  %42 = getelementptr %struct.__ix_bfloat16, ptr addrspace(1) %41, i64 %40
  %43 = or disjoint i32 %37, 1
  %44 = zext nneg i32 %43 to i64
  %45 = mul nsw i64 %8, %44
  %46 = getelementptr %struct.__ix_bfloat16, ptr addrspace(1) %34, i64 %45
  %47 = getelementptr %struct.__ix_bfloat16, ptr addrspace(1) %46, i64 %40
  %48 = load i16, ptr addrspace(1) %42, align 2
  %49 = load i16, ptr addrspace(1) %47, align 2
  %50 = zext i16 %48 to i32
  %51 = zext i16 %49 to i32
  %52 = shl nuw i32 %51, 16
  %53 = or disjoint i32 %52, %50
  %54 = insertelement <2 x i32> poison, i32 %53, i64 0
  %55 = shufflevector <2 x i32> %54, <2 x i32> poison, <2 x i32> zeroinitializer
  %56 = getelementptr i8, ptr addrspace(1) %42, i64 32
  %57 = load i16, ptr addrspace(1) %56, align 2
  %58 = getelementptr i8, ptr addrspace(1) %47, i64 32
  %59 = load i16, ptr addrspace(1) %58, align 2
  %60 = zext i16 %57 to i32
  %61 = zext i16 %59 to i32
  %62 = shl nuw i32 %61, 16
  %63 = or disjoint i32 %62, %60
  %64 = insertelement <2 x i32> poison, i32 %63, i64 0
  %65 = shufflevector <2 x i32> %64, <2 x i32> poison, <2 x i32> zeroinitializer
  %66 = getelementptr i8, ptr addrspace(1) %42, i64 64
  %67 = load i16, ptr addrspace(1) %66, align 2
  %68 = getelementptr i8, ptr addrspace(1) %47, i64 64
  %69 = load i16, ptr addrspace(1) %68, align 2
  %70 = zext i16 %67 to i32
  %71 = zext i16 %69 to i32
  %72 = shl nuw i32 %71, 16
  %73 = or disjoint i32 %72, %70
  %74 = insertelement <2 x i32> poison, i32 %73, i64 0
  %75 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %76 = getelementptr i8, ptr addrspace(1) %42, i64 96
  %77 = load i16, ptr addrspace(1) %76, align 2
  %78 = getelementptr i8, ptr addrspace(1) %47, i64 96
  %79 = load i16, ptr addrspace(1) %78, align 2
  %80 = zext i16 %77 to i32
  %81 = zext i16 %79 to i32
  %82 = shl nuw i32 %81, 16
  %83 = or disjoint i32 %82, %80
  %84 = insertelement <2 x i32> poison, i32 %83, i64 0
  %85 = shufflevector <2 x i32> %84, <2 x i32> poison, <2 x i32> zeroinitializer
  %86 = getelementptr i8, ptr addrspace(1) %42, i64 128
  %87 = load i16, ptr addrspace(1) %86, align 2
  %88 = getelementptr i8, ptr addrspace(1) %47, i64 128
  %89 = load i16, ptr addrspace(1) %88, align 2
  %90 = zext i16 %87 to i32
  %91 = zext i16 %89 to i32
  %92 = shl nuw i32 %91, 16
  %93 = or disjoint i32 %92, %90
  %94 = insertelement <2 x i32> poison, i32 %93, i64 0
  %95 = shufflevector <2 x i32> %94, <2 x i32> poison, <2 x i32> zeroinitializer
  %96 = getelementptr i8, ptr addrspace(1) %42, i64 160
  %97 = load i16, ptr addrspace(1) %96, align 2
  %98 = getelementptr i8, ptr addrspace(1) %47, i64 160
  %99 = load i16, ptr addrspace(1) %98, align 2
  %100 = zext i16 %97 to i32
  %101 = zext i16 %99 to i32
  %102 = shl nuw i32 %101, 16
  %103 = or disjoint i32 %102, %100
  %104 = insertelement <2 x i32> poison, i32 %103, i64 0
  %105 = shufflevector <2 x i32> %104, <2 x i32> poison, <2 x i32> zeroinitializer
  %106 = getelementptr i8, ptr addrspace(1) %42, i64 192
  %107 = load i16, ptr addrspace(1) %106, align 2
  %108 = getelementptr i8, ptr addrspace(1) %47, i64 192
  %109 = load i16, ptr addrspace(1) %108, align 2
  %110 = zext i16 %107 to i32
  %111 = zext i16 %109 to i32
  %112 = shl nuw i32 %111, 16
  %113 = or disjoint i32 %112, %110
  %114 = insertelement <2 x i32> poison, i32 %113, i64 0
  %115 = shufflevector <2 x i32> %114, <2 x i32> poison, <2 x i32> zeroinitializer
  %116 = getelementptr i8, ptr addrspace(1) %42, i64 224
  %117 = load i16, ptr addrspace(1) %116, align 2
  %118 = getelementptr i8, ptr addrspace(1) %47, i64 224
  %119 = load i16, ptr addrspace(1) %118, align 2
  %120 = zext i16 %117 to i32
  %121 = zext i16 %119 to i32
  %122 = shl nuw i32 %121, 16
  %123 = or disjoint i32 %122, %120
  %124 = insertelement <2 x i32> poison, i32 %123, i64 0
  %125 = shufflevector <2 x i32> %124, <2 x i32> poison, <2 x i32> zeroinitializer
  %126 = add i32 %29, %28
  %127 = shl i32 %126, 4
  %128 = tail call noundef i32 @llvm.smin.i32(i32 noundef %127, i32 noundef %26) #3
  %129 = sub nsw i32 %128, %30
  %130 = sdiv i32 %129, 16
  %131 = add i32 %130, %29
  %132 = shl i32 %131, 4
  %133 = mul nsw i64 %6, %24
  %134 = getelementptr inbounds i32, ptr addrspace(1) %4, i64 %133
  %135 = icmp slt i32 %30, %132
  br i1 %135, label %136, label %531

136:                                              ; preds = %32
  %137 = shl nuw nsw i32 %20, 7
  %138 = zext nneg i32 %137 to i64
  %139 = shl nuw nsw i32 %18, 4
  %140 = and i32 %139, 192
  %141 = getelementptr inbounds nuw i32, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 %140
  %142 = getelementptr inbounds nuw i32, ptr addrspace(3) %141, i32 %18
  %143 = xor i32 %18, 4
  %144 = getelementptr inbounds nuw i32, ptr addrspace(3) %141, i32 %143
  %145 = bitcast <2 x i32> %55 to <4 x bfloat>
  %146 = xor i32 %18, 8
  %147 = getelementptr inbounds nuw i32, ptr addrspace(3) %141, i32 %146
  %148 = xor i32 %18, 12
  %149 = getelementptr inbounds nuw i32, ptr addrspace(3) %141, i32 %148
  %150 = bitcast <2 x i32> %65 to <4 x bfloat>
  %151 = getelementptr inbounds nuw i8, ptr addrspace(3) %141, i32 1024
  %152 = getelementptr inbounds nuw i32, ptr addrspace(3) %151, i32 %18
  %153 = getelementptr inbounds nuw i32, ptr addrspace(3) %151, i32 %143
  %154 = bitcast <2 x i32> %75 to <4 x bfloat>
  %155 = getelementptr inbounds nuw i32, ptr addrspace(3) %151, i32 %146
  %156 = getelementptr inbounds nuw i32, ptr addrspace(3) %151, i32 %148
  %157 = bitcast <2 x i32> %85 to <4 x bfloat>
  %158 = getelementptr inbounds nuw i8, ptr addrspace(3) %141, i32 2048
  %159 = getelementptr inbounds nuw i32, ptr addrspace(3) %158, i32 %18
  %160 = getelementptr inbounds nuw i32, ptr addrspace(3) %158, i32 %143
  %161 = bitcast <2 x i32> %95 to <4 x bfloat>
  %162 = getelementptr inbounds nuw i32, ptr addrspace(3) %158, i32 %146
  %163 = getelementptr inbounds nuw i32, ptr addrspace(3) %158, i32 %148
  %164 = bitcast <2 x i32> %105 to <4 x bfloat>
  %165 = getelementptr inbounds nuw i8, ptr addrspace(3) %141, i32 3072
  %166 = getelementptr inbounds nuw i32, ptr addrspace(3) %165, i32 %18
  %167 = getelementptr inbounds nuw i32, ptr addrspace(3) %165, i32 %143
  %168 = bitcast <2 x i32> %115 to <4 x bfloat>
  %169 = getelementptr inbounds nuw i32, ptr addrspace(3) %165, i32 %146
  %170 = getelementptr inbounds nuw i32, ptr addrspace(3) %165, i32 %148
  %171 = bitcast <2 x i32> %125 to <4 x bfloat>
  %172 = xor i32 %18, 2
  %173 = xor i32 %18, 1
  %174 = and i32 %18, 16
  %175 = icmp eq i32 %174, 0
  %176 = shl nuw nsw i32 %174, 1
  %177 = and i32 %18, 32
  %178 = lshr exact i32 %177, 1
  %179 = or disjoint i32 %176, %178
  %180 = or disjoint i32 %179, %23
  %181 = xor i32 %180, 16
  %182 = icmp eq i32 %177, 0
  %183 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 4096), i32 %18
  %184 = getelementptr inbounds nuw i8, ptr addrspace(3) %183, i32 256
  %185 = xor i32 %18, 32
  %186 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 4608), i32 %185
  %187 = getelementptr inbounds nuw i8, ptr addrspace(3) %186, i32 256
  %188 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 5120), i32 %18
  %189 = getelementptr inbounds nuw i8, ptr addrspace(3) %188, i32 256
  %190 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 5632), i32 %185
  %191 = getelementptr inbounds nuw i8, ptr addrspace(3) %190, i32 256
  %192 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 6144), i32 %18
  %193 = getelementptr inbounds nuw i8, ptr addrspace(3) %192, i32 256
  %194 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 6656), i32 %185
  %195 = getelementptr inbounds nuw i8, ptr addrspace(3) %194, i32 256
  %196 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 7168), i32 %18
  %197 = getelementptr inbounds nuw i8, ptr addrspace(3) %196, i32 256
  %198 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 7680), i32 %185
  %199 = getelementptr inbounds nuw i8, ptr addrspace(3) %198, i32 256
  br label %200

200:                                              ; preds = %136, %380
  %201 = phi <4 x float> [ zeroinitializer, %136 ], [ %528, %380 ]
  %202 = phi <4 x float> [ zeroinitializer, %136 ], [ %510, %380 ]
  %203 = phi <4 x float> [ zeroinitializer, %136 ], [ %492, %380 ]
  %204 = phi <4 x float> [ zeroinitializer, %136 ], [ %474, %380 ]
  %205 = phi <4 x float> [ zeroinitializer, %136 ], [ %456, %380 ]
  %206 = phi <4 x float> [ zeroinitializer, %136 ], [ %438, %380 ]
  %207 = phi <4 x float> [ zeroinitializer, %136 ], [ %420, %380 ]
  %208 = phi <4 x float> [ zeroinitializer, %136 ], [ %402, %380 ]
  %209 = phi i32 [ %30, %136 ], [ %529, %380 ]
  %210 = phi float [ 0.000000e+00, %136 ], [ %361, %380 ]
  %211 = phi float [ 0.000000e+00, %136 ], [ %360, %380 ]
  %212 = phi float [ 0xFFF0000000000000, %136 ], [ %319, %380 ]
  %213 = phi float [ 0xFFF0000000000000, %136 ], [ %318, %380 ]
  %214 = ashr exact i32 %209, 4
  %215 = sext i32 %214 to i64
  %216 = getelementptr inbounds i32, ptr addrspace(1) %134, i64 %215
  %217 = load i32, ptr addrspace(1) %216, align 4
  %218 = sext i32 %217 to i64
  %219 = shl nsw i64 %218, 14
  %220 = getelementptr inbounds i8, ptr addrspace(1) %1, i64 %219
  %221 = addrspacecast ptr addrspace(1) %220 to ptr
  %222 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr %221, i64 %138
  %223 = ptrtoint ptr %222 to i64
  %224 = insertelement <2 x i64> poison, i64 %223, i64 0
  %225 = bitcast <2 x i64> %224 to <4 x i32>
  %226 = shufflevector <4 x i32> %225, <4 x i32> <i32 poison, i32 poison, i32 -1, i32 512>, <4 x i32> <i32 0, i32 1, i32 6, i32 7>
  tail call void @llvm.bi.sme.load.16x1b64.colxfb16(i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), <4 x i32> %226, i32 0, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.colxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), i32 1024), <4 x i32> %226, i32 64, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.colxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), i32 2048), <4 x i32> %226, i32 128, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.colxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), i32 3072), <4 x i32> %226, i32 192, i32 0)
  tail call void @llvm.bi.sl.waitcnt(i64 8)
  %227 = getelementptr inbounds i8, ptr addrspace(1) %2, i64 %219
  %228 = addrspacecast ptr addrspace(1) %227 to ptr
  %229 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr %228, i64 %138
  %230 = ptrtoint ptr %229 to i64
  %231 = insertelement <2 x i64> poison, i64 %230, i64 0
  %232 = bitcast <2 x i64> %231 to <4 x i32>
  %233 = shufflevector <4 x i32> %232, <4 x i32> <i32 poison, i32 poison, i32 -1, i32 512>, <4 x i32> <i32 0, i32 1, i32 6, i32 7>
  tail call void @llvm.bi.sme.load.16x1b64.rowxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), i32 4096), <4 x i32> %233, i32 0, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.rowxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), i32 5120), <4 x i32> %233, i32 64, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.rowxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), i32 6144), <4 x i32> %233, i32 128, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.rowxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), i32 7168), <4 x i32> %233, i32 192, i32 0)
  tail call void @llvm.bi.sl.waitcnt(i64 8)
  tail call void @llvm.bi.sl.barrier()
  %234 = load i32, ptr addrspace(3) %142, align 4
  %235 = insertelement <2 x i32> poison, i32 %234, i64 0
  %236 = load i32, ptr addrspace(3) %144, align 4
  %237 = insertelement <2 x i32> %235, i32 %236, i64 1
  %238 = bitcast <2 x i32> %237 to <4 x bfloat>
  %239 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %145, <4 x bfloat> %238, <4 x float> zeroinitializer)
  %240 = load i32, ptr addrspace(3) %147, align 4
  %241 = insertelement <2 x i32> poison, i32 %240, i64 0
  %242 = load i32, ptr addrspace(3) %149, align 4
  %243 = insertelement <2 x i32> %241, i32 %242, i64 1
  %244 = bitcast <2 x i32> %243 to <4 x bfloat>
  %245 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %150, <4 x bfloat> %244, <4 x float> %239)
  %246 = load i32, ptr addrspace(3) %152, align 4
  %247 = insertelement <2 x i32> poison, i32 %246, i64 0
  %248 = load i32, ptr addrspace(3) %153, align 4
  %249 = insertelement <2 x i32> %247, i32 %248, i64 1
  %250 = bitcast <2 x i32> %249 to <4 x bfloat>
  %251 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %154, <4 x bfloat> %250, <4 x float> %245)
  %252 = load i32, ptr addrspace(3) %155, align 4
  %253 = insertelement <2 x i32> poison, i32 %252, i64 0
  %254 = load i32, ptr addrspace(3) %156, align 4
  %255 = insertelement <2 x i32> %253, i32 %254, i64 1
  %256 = bitcast <2 x i32> %255 to <4 x bfloat>
  %257 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %157, <4 x bfloat> %256, <4 x float> %251)
  %258 = load i32, ptr addrspace(3) %159, align 4
  %259 = insertelement <2 x i32> poison, i32 %258, i64 0
  %260 = load i32, ptr addrspace(3) %160, align 4
  %261 = insertelement <2 x i32> %259, i32 %260, i64 1
  %262 = bitcast <2 x i32> %261 to <4 x bfloat>
  %263 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %161, <4 x bfloat> %262, <4 x float> %257)
  %264 = load i32, ptr addrspace(3) %162, align 4
  %265 = insertelement <2 x i32> poison, i32 %264, i64 0
  %266 = load i32, ptr addrspace(3) %163, align 4
  %267 = insertelement <2 x i32> %265, i32 %266, i64 1
  %268 = bitcast <2 x i32> %267 to <4 x bfloat>
  %269 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %164, <4 x bfloat> %268, <4 x float> %263)
  %270 = load i32, ptr addrspace(3) %166, align 4
  %271 = insertelement <2 x i32> poison, i32 %270, i64 0
  %272 = load i32, ptr addrspace(3) %167, align 4
  %273 = insertelement <2 x i32> %271, i32 %272, i64 1
  %274 = bitcast <2 x i32> %273 to <4 x bfloat>
  %275 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %168, <4 x bfloat> %274, <4 x float> %269)
  %276 = load i32, ptr addrspace(3) %169, align 4
  %277 = insertelement <2 x i32> poison, i32 %276, i64 0
  %278 = load i32, ptr addrspace(3) %170, align 4
  %279 = insertelement <2 x i32> %277, i32 %278, i64 1
  %280 = bitcast <2 x i32> %279 to <4 x bfloat>
  %281 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %171, <4 x bfloat> %280, <4 x float> %275)
  %282 = extractelement <4 x float> %281, i64 0
  %283 = fmul contract float %5, %282
  %284 = extractelement <4 x float> %281, i64 1
  %285 = fmul contract float %5, %284
  %286 = bitcast float %283 to i32
  %287 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %286, i32 %146)
  %288 = bitcast i32 %287 to float
  %289 = tail call noundef float @llvm.maxnum.f32(float %283, float %288)
  %290 = bitcast float %285 to i32
  %291 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %290, i32 %146)
  %292 = bitcast i32 %291 to float
  %293 = tail call noundef float @llvm.maxnum.f32(float %285, float %292)
  %294 = bitcast float %289 to i32
  %295 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %294, i32 %143)
  %296 = bitcast i32 %295 to float
  %297 = tail call noundef float @llvm.maxnum.f32(float %289, float %296)
  %298 = bitcast float %293 to i32
  %299 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %298, i32 %143)
  %300 = bitcast i32 %299 to float
  %301 = tail call noundef float @llvm.maxnum.f32(float %293, float %300)
  %302 = bitcast float %297 to i32
  %303 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %302, i32 %172)
  %304 = bitcast i32 %303 to float
  %305 = tail call noundef float @llvm.maxnum.f32(float %297, float %304)
  %306 = bitcast float %301 to i32
  %307 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %306, i32 %172)
  %308 = bitcast i32 %307 to float
  %309 = tail call noundef float @llvm.maxnum.f32(float %301, float %308)
  %310 = bitcast float %305 to i32
  %311 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %310, i32 %173)
  %312 = bitcast i32 %311 to float
  %313 = tail call noundef float @llvm.maxnum.f32(float %305, float %312)
  %314 = bitcast float %309 to i32
  %315 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %314, i32 %173)
  %316 = bitcast i32 %315 to float
  %317 = tail call noundef float @llvm.maxnum.f32(float %309, float %316)
  %318 = tail call noundef float @llvm.maxnum.f32(float %213, float %313)
  %319 = tail call noundef float @llvm.maxnum.f32(float %212, float %317)
  %320 = fsub contract float %283, %318
  %321 = tail call noundef float @llvm.nvvm.ex2.approx.f32(float %320)
  %322 = fsub contract float %285, %319
  %323 = tail call noundef float @llvm.nvvm.ex2.approx.f32(float %322)
  %324 = bitcast float %321 to i32
  %325 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %324, i32 %146)
  %326 = bitcast i32 %325 to float
  %327 = fadd contract float %321, %326
  %328 = bitcast float %323 to i32
  %329 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %328, i32 %146)
  %330 = bitcast i32 %329 to float
  %331 = fadd contract float %323, %330
  %332 = bitcast float %327 to i32
  %333 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %332, i32 %143)
  %334 = bitcast i32 %333 to float
  %335 = fadd contract float %327, %334
  %336 = bitcast float %331 to i32
  %337 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %336, i32 %143)
  %338 = bitcast i32 %337 to float
  %339 = fadd contract float %331, %338
  %340 = bitcast float %335 to i32
  %341 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %340, i32 %172)
  %342 = bitcast i32 %341 to float
  %343 = fadd contract float %335, %342
  %344 = bitcast float %339 to i32
  %345 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %344, i32 %172)
  %346 = bitcast i32 %345 to float
  %347 = fadd contract float %339, %346
  %348 = bitcast float %343 to i32
  %349 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %348, i32 %173)
  %350 = bitcast i32 %349 to float
  %351 = fadd contract float %343, %350
  %352 = bitcast float %347 to i32
  %353 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %352, i32 %173)
  %354 = bitcast i32 %353 to float
  %355 = fadd contract float %347, %354
  %356 = fsub contract float %213, %318
  %357 = tail call noundef float @llvm.nvvm.ex2.approx.f32(float %356)
  %358 = fsub contract float %212, %319
  %359 = tail call noundef float @llvm.nvvm.ex2.approx.f32(float %358)
  %360 = tail call noundef float @llvm.fma.f32(float %211, float %357, float %351)
  %361 = tail call noundef float @llvm.fma.f32(float %210, float %359, float %355)
  %362 = fptrunc contract float %321 to bfloat
  %363 = bitcast bfloat %362 to i16
  %364 = fptrunc contract float %323 to bfloat
  %365 = bitcast bfloat %364 to i16
  %366 = select i1 %175, i16 %363, i16 %365
  %367 = zext i16 %366 to i32
  %368 = select i1 %175, i16 %365, i16 %363
  %369 = zext i16 %368 to i32
  %370 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 range(i32 0, 65536) %367, i32 range(i32 0, 64) %180)
  %371 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 range(i32 0, 65536) %369, i32 range(i32 0, 64) %181)
  br i1 %182, label %376, label %372

372:                                              ; preds = %200
  %373 = and i32 %371, 65535
  %374 = shl i32 %370, 16
  %375 = or disjoint i32 %373, %374
  br label %380

376:                                              ; preds = %200
  %377 = and i32 %370, 65535
  %378 = shl i32 %371, 16
  %379 = or disjoint i32 %378, %377
  br label %380

380:                                              ; preds = %372, %376
  %381 = phi i32 [ %375, %372 ], [ %379, %376 ]
  %382 = insertelement <2 x i32> poison, i32 %381, i64 0
  %383 = shufflevector <2 x i32> %382, <2 x i32> poison, <2 x i32> zeroinitializer
  %384 = bitcast <2 x i32> %383 to <4 x bfloat>
  %385 = load i32, ptr addrspace(3) %183, align 4
  %386 = insertelement <2 x i32> poison, i32 %385, i64 0
  %387 = load i32, ptr addrspace(3) %184, align 4
  %388 = insertelement <2 x i32> %386, i32 %387, i64 1
  %389 = extractelement <4 x float> %208, i64 0
  %390 = fmul contract float %357, %389
  %391 = insertelement <4 x float> poison, float %390, i64 0
  %392 = extractelement <4 x float> %208, i64 1
  %393 = fmul contract float %359, %392
  %394 = insertelement <4 x float> %391, float %393, i64 1
  %395 = extractelement <4 x float> %208, i64 2
  %396 = fmul contract float %357, %395
  %397 = insertelement <4 x float> %394, float %396, i64 2
  %398 = extractelement <4 x float> %208, i64 3
  %399 = fmul contract float %359, %398
  %400 = insertelement <4 x float> %397, float %399, i64 3
  %401 = bitcast <2 x i32> %388 to <4 x bfloat>
  %402 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %384, <4 x bfloat> %401, <4 x float> %400)
  %403 = load i32, ptr addrspace(3) %186, align 4
  %404 = insertelement <2 x i32> poison, i32 %403, i64 0
  %405 = load i32, ptr addrspace(3) %187, align 4
  %406 = insertelement <2 x i32> %404, i32 %405, i64 1
  %407 = extractelement <4 x float> %207, i64 0
  %408 = fmul contract float %357, %407
  %409 = insertelement <4 x float> poison, float %408, i64 0
  %410 = extractelement <4 x float> %207, i64 1
  %411 = fmul contract float %359, %410
  %412 = insertelement <4 x float> %409, float %411, i64 1
  %413 = extractelement <4 x float> %207, i64 2
  %414 = fmul contract float %357, %413
  %415 = insertelement <4 x float> %412, float %414, i64 2
  %416 = extractelement <4 x float> %207, i64 3
  %417 = fmul contract float %359, %416
  %418 = insertelement <4 x float> %415, float %417, i64 3
  %419 = bitcast <2 x i32> %406 to <4 x bfloat>
  %420 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %384, <4 x bfloat> %419, <4 x float> %418)
  %421 = load i32, ptr addrspace(3) %188, align 4
  %422 = insertelement <2 x i32> poison, i32 %421, i64 0
  %423 = load i32, ptr addrspace(3) %189, align 4
  %424 = insertelement <2 x i32> %422, i32 %423, i64 1
  %425 = extractelement <4 x float> %206, i64 0
  %426 = fmul contract float %357, %425
  %427 = insertelement <4 x float> poison, float %426, i64 0
  %428 = extractelement <4 x float> %206, i64 1
  %429 = fmul contract float %359, %428
  %430 = insertelement <4 x float> %427, float %429, i64 1
  %431 = extractelement <4 x float> %206, i64 2
  %432 = fmul contract float %357, %431
  %433 = insertelement <4 x float> %430, float %432, i64 2
  %434 = extractelement <4 x float> %206, i64 3
  %435 = fmul contract float %359, %434
  %436 = insertelement <4 x float> %433, float %435, i64 3
  %437 = bitcast <2 x i32> %424 to <4 x bfloat>
  %438 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %384, <4 x bfloat> %437, <4 x float> %436)
  %439 = load i32, ptr addrspace(3) %190, align 4
  %440 = insertelement <2 x i32> poison, i32 %439, i64 0
  %441 = load i32, ptr addrspace(3) %191, align 4
  %442 = insertelement <2 x i32> %440, i32 %441, i64 1
  %443 = extractelement <4 x float> %205, i64 0
  %444 = fmul contract float %357, %443
  %445 = insertelement <4 x float> poison, float %444, i64 0
  %446 = extractelement <4 x float> %205, i64 1
  %447 = fmul contract float %359, %446
  %448 = insertelement <4 x float> %445, float %447, i64 1
  %449 = extractelement <4 x float> %205, i64 2
  %450 = fmul contract float %357, %449
  %451 = insertelement <4 x float> %448, float %450, i64 2
  %452 = extractelement <4 x float> %205, i64 3
  %453 = fmul contract float %359, %452
  %454 = insertelement <4 x float> %451, float %453, i64 3
  %455 = bitcast <2 x i32> %442 to <4 x bfloat>
  %456 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %384, <4 x bfloat> %455, <4 x float> %454)
  %457 = load i32, ptr addrspace(3) %192, align 4
  %458 = insertelement <2 x i32> poison, i32 %457, i64 0
  %459 = load i32, ptr addrspace(3) %193, align 4
  %460 = insertelement <2 x i32> %458, i32 %459, i64 1
  %461 = extractelement <4 x float> %204, i64 0
  %462 = fmul contract float %357, %461
  %463 = insertelement <4 x float> poison, float %462, i64 0
  %464 = extractelement <4 x float> %204, i64 1
  %465 = fmul contract float %359, %464
  %466 = insertelement <4 x float> %463, float %465, i64 1
  %467 = extractelement <4 x float> %204, i64 2
  %468 = fmul contract float %357, %467
  %469 = insertelement <4 x float> %466, float %468, i64 2
  %470 = extractelement <4 x float> %204, i64 3
  %471 = fmul contract float %359, %470
  %472 = insertelement <4 x float> %469, float %471, i64 3
  %473 = bitcast <2 x i32> %460 to <4 x bfloat>
  %474 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %384, <4 x bfloat> %473, <4 x float> %472)
  %475 = load i32, ptr addrspace(3) %194, align 4
  %476 = insertelement <2 x i32> poison, i32 %475, i64 0
  %477 = load i32, ptr addrspace(3) %195, align 4
  %478 = insertelement <2 x i32> %476, i32 %477, i64 1
  %479 = extractelement <4 x float> %203, i64 0
  %480 = fmul contract float %357, %479
  %481 = insertelement <4 x float> poison, float %480, i64 0
  %482 = extractelement <4 x float> %203, i64 1
  %483 = fmul contract float %359, %482
  %484 = insertelement <4 x float> %481, float %483, i64 1
  %485 = extractelement <4 x float> %203, i64 2
  %486 = fmul contract float %357, %485
  %487 = insertelement <4 x float> %484, float %486, i64 2
  %488 = extractelement <4 x float> %203, i64 3
  %489 = fmul contract float %359, %488
  %490 = insertelement <4 x float> %487, float %489, i64 3
  %491 = bitcast <2 x i32> %478 to <4 x bfloat>
  %492 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %384, <4 x bfloat> %491, <4 x float> %490)
  %493 = load i32, ptr addrspace(3) %196, align 4
  %494 = insertelement <2 x i32> poison, i32 %493, i64 0
  %495 = load i32, ptr addrspace(3) %197, align 4
  %496 = insertelement <2 x i32> %494, i32 %495, i64 1
  %497 = extractelement <4 x float> %202, i64 0
  %498 = fmul contract float %357, %497
  %499 = insertelement <4 x float> poison, float %498, i64 0
  %500 = extractelement <4 x float> %202, i64 1
  %501 = fmul contract float %359, %500
  %502 = insertelement <4 x float> %499, float %501, i64 1
  %503 = extractelement <4 x float> %202, i64 2
  %504 = fmul contract float %357, %503
  %505 = insertelement <4 x float> %502, float %504, i64 2
  %506 = extractelement <4 x float> %202, i64 3
  %507 = fmul contract float %359, %506
  %508 = insertelement <4 x float> %505, float %507, i64 3
  %509 = bitcast <2 x i32> %496 to <4 x bfloat>
  %510 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %384, <4 x bfloat> %509, <4 x float> %508)
  %511 = load i32, ptr addrspace(3) %198, align 4
  %512 = insertelement <2 x i32> poison, i32 %511, i64 0
  %513 = load i32, ptr addrspace(3) %199, align 4
  %514 = insertelement <2 x i32> %512, i32 %513, i64 1
  %515 = extractelement <4 x float> %201, i64 0
  %516 = fmul contract float %357, %515
  %517 = insertelement <4 x float> poison, float %516, i64 0
  %518 = extractelement <4 x float> %201, i64 1
  %519 = fmul contract float %359, %518
  %520 = insertelement <4 x float> %517, float %519, i64 1
  %521 = extractelement <4 x float> %201, i64 2
  %522 = fmul contract float %357, %521
  %523 = insertelement <4 x float> %520, float %522, i64 2
  %524 = extractelement <4 x float> %201, i64 3
  %525 = fmul contract float %359, %524
  %526 = insertelement <4 x float> %523, float %525, i64 3
  %527 = bitcast <2 x i32> %514 to <4 x bfloat>
  %528 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %384, <4 x bfloat> %527, <4 x float> %526)
  tail call void @llvm.bi.sl.barrier()
  %529 = add nsw i32 %209, 16
  %530 = icmp slt i32 %529, %132
  br i1 %530, label %200, label %531, !llvm.loop !8

531:                                              ; preds = %380, %32
  %532 = phi <4 x float> [ zeroinitializer, %32 ], [ %528, %380 ]
  %533 = phi <4 x float> [ zeroinitializer, %32 ], [ %510, %380 ]
  %534 = phi <4 x float> [ zeroinitializer, %32 ], [ %492, %380 ]
  %535 = phi <4 x float> [ zeroinitializer, %32 ], [ %474, %380 ]
  %536 = phi <4 x float> [ zeroinitializer, %32 ], [ %456, %380 ]
  %537 = phi <4 x float> [ zeroinitializer, %32 ], [ %438, %380 ]
  %538 = phi <4 x float> [ zeroinitializer, %32 ], [ %420, %380 ]
  %539 = phi <4 x float> [ zeroinitializer, %32 ], [ %402, %380 ]
  %540 = phi float [ 0xFFF0000000000000, %32 ], [ %318, %380 ]
  %541 = phi float [ 0xFFF0000000000000, %32 ], [ %319, %380 ]
  %542 = phi float [ 0.000000e+00, %32 ], [ %360, %380 ]
  %543 = phi float [ 0.000000e+00, %32 ], [ %361, %380 ]
  %544 = icmp slt i32 %132, %128
  br i1 %544, label %545, label %989

545:                                              ; preds = %531
  %546 = ashr exact i32 %132, 4
  %547 = sext i32 %546 to i64
  %548 = getelementptr inbounds i32, ptr addrspace(1) %134, i64 %547
  %549 = load i32, ptr addrspace(1) %548, align 4
  %550 = sub nsw i32 %128, %132
  %551 = sext i32 %549 to i64
  %552 = shl nsw i64 %551, 14
  %553 = getelementptr inbounds i8, ptr addrspace(1) %1, i64 %552
  %554 = addrspacecast ptr addrspace(1) %553 to ptr
  %555 = shl nuw nsw i32 %20, 7
  %556 = zext nneg i32 %555 to i64
  %557 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr %554, i64 %556
  %558 = ptrtoint ptr %557 to i64
  %559 = insertelement <2 x i64> poison, i64 %558, i64 0
  %560 = bitcast <2 x i64> %559 to <4 x i32>
  %561 = shufflevector <4 x i32> %560, <4 x i32> <i32 poison, i32 poison, i32 -1, i32 512>, <4 x i32> <i32 0, i32 1, i32 6, i32 7>
  tail call void @llvm.bi.sme.load.16x1b64.colxfb16(i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), <4 x i32> %561, i32 0, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.colxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), i32 1024), <4 x i32> %561, i32 64, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.colxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), i32 2048), <4 x i32> %561, i32 128, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.colxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), i32 3072), <4 x i32> %561, i32 192, i32 0)
  tail call void @llvm.bi.sl.waitcnt(i64 8)
  %562 = getelementptr inbounds i8, ptr addrspace(1) %2, i64 %552
  %563 = addrspacecast ptr addrspace(1) %562 to ptr
  %564 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr %563, i64 %556
  %565 = ptrtoint ptr %564 to i64
  %566 = insertelement <2 x i64> poison, i64 %565, i64 0
  %567 = bitcast <2 x i64> %566 to <4 x i32>
  %568 = shufflevector <4 x i32> %567, <4 x i32> <i32 poison, i32 poison, i32 -1, i32 512>, <4 x i32> <i32 0, i32 1, i32 6, i32 7>
  tail call void @llvm.bi.sme.load.16x1b64.rowxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), i32 4096), <4 x i32> %568, i32 0, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.rowxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), i32 5120), <4 x i32> %568, i32 64, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.rowxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), i32 6144), <4 x i32> %568, i32 128, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.rowxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage to ptr) to i32), i32 7168), <4 x i32> %568, i32 192, i32 0)
  tail call void @llvm.bi.sl.waitcnt(i64 8)
  tail call void @llvm.bi.sl.barrier()
  %569 = icmp ult i32 %550, 16
  br i1 %569, label %570, label %629

570:                                              ; preds = %545, %593
  %571 = phi i32 [ %594, %593 ], [ %18, %545 ]
  %572 = lshr i32 %571, 6
  %573 = icmp samesign ult i32 %572, %550
  br i1 %573, label %593, label %574

574:                                              ; preds = %570
  %575 = shl nuw nsw i32 %571, 1
  %576 = shl nuw nsw i32 %571, 5
  %577 = lshr i32 %571, 8
  %578 = shl nuw nsw i32 %577, 7
  %579 = and i32 %576, 1632
  %580 = add nuw nsw i32 %579, %578
  %581 = shl nuw nsw i32 %572, 1
  %582 = xor i32 %581, %575
  %583 = and i32 %582, 16
  %584 = or disjoint i32 %583, %580
  %585 = shl nuw nsw i32 %577, 3
  %586 = xor i32 %585, %575
  %587 = and i32 %586, 8
  %588 = or disjoint i32 %584, %587
  %589 = and i32 %581, 6
  %590 = or disjoint i32 %588, %589
  %591 = lshr exact i32 %590, 1
  %592 = getelementptr inbounds nuw i32, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 %591
  store i32 0, ptr addrspace(3) %592, align 4
  br label %593

593:                                              ; preds = %574, %570
  %594 = add nuw nsw i32 %571, 64
  %595 = icmp samesign ult i32 %571, 960
  br i1 %595, label %570, label %596, !llvm.loop !10

596:                                              ; preds = %593, %625
  %597 = phi i32 [ %626, %625 ], [ %18, %593 ]
  %598 = lshr i32 %597, 6
  %599 = and i32 %598, 14
  %600 = lshr i32 %597, 4
  %601 = shl nuw nsw i32 %600, 8
  %602 = and i32 %601, 1792
  %603 = shl nuw nsw i32 %599, 4
  %604 = and i32 %603, 128
  %605 = or disjoint i32 %604, %602
  %606 = shl nuw nsw i32 %597, 1
  %607 = and i32 %606, 30
  %608 = shl nuw nsw i32 %600, 6
  %609 = or disjoint i32 %608, %607
  %610 = add nuw nsw i32 %609, %603
  %611 = and i32 %610, 126
  %612 = or disjoint i32 %605, %611
  %613 = lshr exact i32 %612, 1
  %614 = or disjoint i32 %613, 1024
  %615 = icmp samesign ult i32 %599, %550
  br i1 %615, label %618, label %616

616:                                              ; preds = %596
  %617 = getelementptr inbounds nuw i32, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 %614
  store i32 0, ptr addrspace(3) %617, align 4
  br label %625

618:                                              ; preds = %596
  %619 = or disjoint i32 %599, 1
  %620 = icmp samesign ult i32 %619, %550
  br i1 %620, label %625, label %621

621:                                              ; preds = %618
  %622 = getelementptr inbounds nuw i32, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 %614
  %623 = load i32, ptr addrspace(3) %622, align 4
  %624 = and i32 %623, 65535
  store i32 %624, ptr addrspace(3) %622, align 4
  br label %625

625:                                              ; preds = %621, %618, %616
  %626 = add nuw nsw i32 %597, 64
  %627 = icmp samesign ult i32 %597, 960
  br i1 %627, label %596, label %628, !llvm.loop !11

628:                                              ; preds = %625
  tail call void @llvm.bi.sl.barrier()
  br label %629

629:                                              ; preds = %628, %545
  %630 = shl nuw nsw i32 %18, 4
  %631 = and i32 %630, 192
  %632 = getelementptr inbounds nuw i32, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 %631
  %633 = getelementptr inbounds nuw i32, ptr addrspace(3) %632, i32 %18
  %634 = load i32, ptr addrspace(3) %633, align 4
  %635 = insertelement <2 x i32> poison, i32 %634, i64 0
  %636 = xor i32 %18, 4
  %637 = getelementptr inbounds nuw i32, ptr addrspace(3) %632, i32 %636
  %638 = load i32, ptr addrspace(3) %637, align 4
  %639 = insertelement <2 x i32> %635, i32 %638, i64 1
  %640 = bitcast <2 x i32> %55 to <4 x bfloat>
  %641 = bitcast <2 x i32> %639 to <4 x bfloat>
  %642 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %640, <4 x bfloat> %641, <4 x float> zeroinitializer)
  %643 = xor i32 %18, 8
  %644 = getelementptr inbounds nuw i32, ptr addrspace(3) %632, i32 %643
  %645 = load i32, ptr addrspace(3) %644, align 4
  %646 = insertelement <2 x i32> poison, i32 %645, i64 0
  %647 = xor i32 %18, 12
  %648 = getelementptr inbounds nuw i32, ptr addrspace(3) %632, i32 %647
  %649 = load i32, ptr addrspace(3) %648, align 4
  %650 = insertelement <2 x i32> %646, i32 %649, i64 1
  %651 = bitcast <2 x i32> %65 to <4 x bfloat>
  %652 = bitcast <2 x i32> %650 to <4 x bfloat>
  %653 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %651, <4 x bfloat> %652, <4 x float> %642)
  %654 = getelementptr inbounds nuw i8, ptr addrspace(3) %632, i32 1024
  %655 = getelementptr inbounds nuw i32, ptr addrspace(3) %654, i32 %18
  %656 = load i32, ptr addrspace(3) %655, align 4
  %657 = insertelement <2 x i32> poison, i32 %656, i64 0
  %658 = getelementptr inbounds nuw i32, ptr addrspace(3) %654, i32 %636
  %659 = load i32, ptr addrspace(3) %658, align 4
  %660 = insertelement <2 x i32> %657, i32 %659, i64 1
  %661 = bitcast <2 x i32> %75 to <4 x bfloat>
  %662 = bitcast <2 x i32> %660 to <4 x bfloat>
  %663 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %661, <4 x bfloat> %662, <4 x float> %653)
  %664 = getelementptr inbounds nuw i32, ptr addrspace(3) %654, i32 %643
  %665 = load i32, ptr addrspace(3) %664, align 4
  %666 = insertelement <2 x i32> poison, i32 %665, i64 0
  %667 = getelementptr inbounds nuw i32, ptr addrspace(3) %654, i32 %647
  %668 = load i32, ptr addrspace(3) %667, align 4
  %669 = insertelement <2 x i32> %666, i32 %668, i64 1
  %670 = bitcast <2 x i32> %85 to <4 x bfloat>
  %671 = bitcast <2 x i32> %669 to <4 x bfloat>
  %672 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %670, <4 x bfloat> %671, <4 x float> %663)
  %673 = getelementptr inbounds nuw i8, ptr addrspace(3) %632, i32 2048
  %674 = getelementptr inbounds nuw i32, ptr addrspace(3) %673, i32 %18
  %675 = load i32, ptr addrspace(3) %674, align 4
  %676 = insertelement <2 x i32> poison, i32 %675, i64 0
  %677 = getelementptr inbounds nuw i32, ptr addrspace(3) %673, i32 %636
  %678 = load i32, ptr addrspace(3) %677, align 4
  %679 = insertelement <2 x i32> %676, i32 %678, i64 1
  %680 = bitcast <2 x i32> %95 to <4 x bfloat>
  %681 = bitcast <2 x i32> %679 to <4 x bfloat>
  %682 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %680, <4 x bfloat> %681, <4 x float> %672)
  %683 = getelementptr inbounds nuw i32, ptr addrspace(3) %673, i32 %643
  %684 = load i32, ptr addrspace(3) %683, align 4
  %685 = insertelement <2 x i32> poison, i32 %684, i64 0
  %686 = getelementptr inbounds nuw i32, ptr addrspace(3) %673, i32 %647
  %687 = load i32, ptr addrspace(3) %686, align 4
  %688 = insertelement <2 x i32> %685, i32 %687, i64 1
  %689 = bitcast <2 x i32> %105 to <4 x bfloat>
  %690 = bitcast <2 x i32> %688 to <4 x bfloat>
  %691 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %689, <4 x bfloat> %690, <4 x float> %682)
  %692 = getelementptr inbounds nuw i8, ptr addrspace(3) %632, i32 3072
  %693 = getelementptr inbounds nuw i32, ptr addrspace(3) %692, i32 %18
  %694 = load i32, ptr addrspace(3) %693, align 4
  %695 = insertelement <2 x i32> poison, i32 %694, i64 0
  %696 = getelementptr inbounds nuw i32, ptr addrspace(3) %692, i32 %636
  %697 = load i32, ptr addrspace(3) %696, align 4
  %698 = insertelement <2 x i32> %695, i32 %697, i64 1
  %699 = bitcast <2 x i32> %115 to <4 x bfloat>
  %700 = bitcast <2 x i32> %698 to <4 x bfloat>
  %701 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %699, <4 x bfloat> %700, <4 x float> %691)
  %702 = getelementptr inbounds nuw i32, ptr addrspace(3) %692, i32 %643
  %703 = load i32, ptr addrspace(3) %702, align 4
  %704 = insertelement <2 x i32> poison, i32 %703, i64 0
  %705 = getelementptr inbounds nuw i32, ptr addrspace(3) %692, i32 %647
  %706 = load i32, ptr addrspace(3) %705, align 4
  %707 = insertelement <2 x i32> %704, i32 %706, i64 1
  %708 = bitcast <2 x i32> %125 to <4 x bfloat>
  %709 = bitcast <2 x i32> %707 to <4 x bfloat>
  %710 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %708, <4 x bfloat> %709, <4 x float> %701)
  %711 = icmp ult i32 %23, %550
  %712 = extractelement <4 x float> %710, i64 0
  %713 = fmul contract float %5, %712
  %714 = select i1 %711, float %713, float 0xFFF0000000000000
  %715 = extractelement <4 x float> %710, i64 1
  %716 = fmul contract float %5, %715
  %717 = select contract i1 %711, float %716, float 0xFFF0000000000000
  %718 = bitcast float %714 to i32
  %719 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %718, i32 %643)
  %720 = bitcast i32 %719 to float
  %721 = tail call noundef float @llvm.maxnum.f32(float %714, float %720)
  %722 = bitcast float %717 to i32
  %723 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %722, i32 %643)
  %724 = bitcast i32 %723 to float
  %725 = tail call noundef float @llvm.maxnum.f32(float %717, float %724)
  %726 = bitcast float %721 to i32
  %727 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %726, i32 %636)
  %728 = bitcast i32 %727 to float
  %729 = tail call noundef float @llvm.maxnum.f32(float %721, float %728)
  %730 = bitcast float %725 to i32
  %731 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %730, i32 %636)
  %732 = bitcast i32 %731 to float
  %733 = tail call noundef float @llvm.maxnum.f32(float %725, float %732)
  %734 = xor i32 %18, 2
  %735 = bitcast float %729 to i32
  %736 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %735, i32 %734)
  %737 = bitcast i32 %736 to float
  %738 = tail call noundef float @llvm.maxnum.f32(float %729, float %737)
  %739 = bitcast float %733 to i32
  %740 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %739, i32 %734)
  %741 = bitcast i32 %740 to float
  %742 = tail call noundef float @llvm.maxnum.f32(float %733, float %741)
  %743 = xor i32 %18, 1
  %744 = bitcast float %738 to i32
  %745 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %744, i32 %743)
  %746 = bitcast i32 %745 to float
  %747 = tail call noundef float @llvm.maxnum.f32(float %738, float %746)
  %748 = bitcast float %742 to i32
  %749 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %748, i32 %743)
  %750 = bitcast i32 %749 to float
  %751 = tail call noundef float @llvm.maxnum.f32(float %742, float %750)
  %752 = tail call noundef float @llvm.maxnum.f32(float %540, float %747)
  %753 = tail call noundef float @llvm.maxnum.f32(float %541, float %751)
  %754 = fsub contract float %714, %752
  %755 = tail call noundef float @llvm.nvvm.ex2.approx.f32(float %754)
  %756 = fsub contract float %717, %753
  %757 = tail call noundef float @llvm.nvvm.ex2.approx.f32(float %756)
  %758 = bitcast float %755 to i32
  %759 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %758, i32 %643)
  %760 = bitcast i32 %759 to float
  %761 = fadd contract float %755, %760
  %762 = bitcast float %757 to i32
  %763 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %762, i32 %643)
  %764 = bitcast i32 %763 to float
  %765 = fadd contract float %757, %764
  %766 = bitcast float %761 to i32
  %767 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %766, i32 %636)
  %768 = bitcast i32 %767 to float
  %769 = fadd contract float %761, %768
  %770 = bitcast float %765 to i32
  %771 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %770, i32 %636)
  %772 = bitcast i32 %771 to float
  %773 = fadd contract float %765, %772
  %774 = bitcast float %769 to i32
  %775 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %774, i32 %734)
  %776 = bitcast i32 %775 to float
  %777 = fadd contract float %769, %776
  %778 = bitcast float %773 to i32
  %779 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %778, i32 %734)
  %780 = bitcast i32 %779 to float
  %781 = fadd contract float %773, %780
  %782 = bitcast float %777 to i32
  %783 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %782, i32 %743)
  %784 = bitcast i32 %783 to float
  %785 = fadd contract float %777, %784
  %786 = bitcast float %781 to i32
  %787 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %786, i32 %743)
  %788 = bitcast i32 %787 to float
  %789 = fadd contract float %781, %788
  %790 = fsub contract float %540, %752
  %791 = tail call noundef float @llvm.nvvm.ex2.approx.f32(float %790)
  %792 = fsub contract float %541, %753
  %793 = tail call noundef float @llvm.nvvm.ex2.approx.f32(float %792)
  %794 = tail call noundef float @llvm.fma.f32(float %542, float %791, float %785)
  %795 = tail call noundef float @llvm.fma.f32(float %543, float %793, float %789)
  %796 = fptrunc contract float %755 to bfloat
  %797 = bitcast bfloat %796 to i16
  %798 = fptrunc contract float %757 to bfloat
  %799 = bitcast bfloat %798 to i16
  %800 = and i32 %18, 16
  %801 = icmp eq i32 %800, 0
  %802 = select i1 %801, i16 %797, i16 %799
  %803 = zext i16 %802 to i32
  %804 = select i1 %801, i16 %799, i16 %797
  %805 = zext i16 %804 to i32
  %806 = shl nuw nsw i32 %800, 1
  %807 = and i32 %18, 32
  %808 = lshr exact i32 %807, 1
  %809 = or disjoint i32 %806, %808
  %810 = or disjoint i32 %809, %23
  %811 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 range(i32 0, 65536) %803, i32 range(i32 0, 64) %810)
  %812 = xor i32 %810, 16
  %813 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 range(i32 0, 65536) %805, i32 range(i32 0, 64) %812)
  %814 = icmp eq i32 %807, 0
  br i1 %814, label %819, label %815

815:                                              ; preds = %629
  %816 = and i32 %813, 65535
  %817 = shl i32 %811, 16
  %818 = or disjoint i32 %816, %817
  br label %823

819:                                              ; preds = %629
  %820 = and i32 %811, 65535
  %821 = shl i32 %813, 16
  %822 = or disjoint i32 %821, %820
  br label %823

823:                                              ; preds = %815, %819
  %824 = phi i32 [ %818, %815 ], [ %822, %819 ]
  %825 = insertelement <2 x i32> poison, i32 %824, i64 0
  %826 = shufflevector <2 x i32> %825, <2 x i32> poison, <2 x i32> zeroinitializer
  %827 = bitcast <2 x i32> %826 to <4 x bfloat>
  %828 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 4096), i32 %18
  %829 = load i32, ptr addrspace(3) %828, align 4
  %830 = insertelement <2 x i32> poison, i32 %829, i64 0
  %831 = getelementptr inbounds nuw i8, ptr addrspace(3) %828, i32 256
  %832 = load i32, ptr addrspace(3) %831, align 4
  %833 = insertelement <2 x i32> %830, i32 %832, i64 1
  %834 = extractelement <4 x float> %539, i64 0
  %835 = fmul contract float %791, %834
  %836 = insertelement <4 x float> poison, float %835, i64 0
  %837 = extractelement <4 x float> %539, i64 1
  %838 = fmul contract float %793, %837
  %839 = insertelement <4 x float> %836, float %838, i64 1
  %840 = extractelement <4 x float> %539, i64 2
  %841 = fmul contract float %791, %840
  %842 = insertelement <4 x float> %839, float %841, i64 2
  %843 = extractelement <4 x float> %539, i64 3
  %844 = fmul contract float %793, %843
  %845 = insertelement <4 x float> %842, float %844, i64 3
  %846 = bitcast <2 x i32> %833 to <4 x bfloat>
  %847 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %827, <4 x bfloat> %846, <4 x float> %845)
  %848 = xor i32 %18, 32
  %849 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 4608), i32 %848
  %850 = load i32, ptr addrspace(3) %849, align 4
  %851 = insertelement <2 x i32> poison, i32 %850, i64 0
  %852 = getelementptr inbounds nuw i8, ptr addrspace(3) %849, i32 256
  %853 = load i32, ptr addrspace(3) %852, align 4
  %854 = insertelement <2 x i32> %851, i32 %853, i64 1
  %855 = extractelement <4 x float> %538, i64 0
  %856 = fmul contract float %791, %855
  %857 = insertelement <4 x float> poison, float %856, i64 0
  %858 = extractelement <4 x float> %538, i64 1
  %859 = fmul contract float %793, %858
  %860 = insertelement <4 x float> %857, float %859, i64 1
  %861 = extractelement <4 x float> %538, i64 2
  %862 = fmul contract float %791, %861
  %863 = insertelement <4 x float> %860, float %862, i64 2
  %864 = extractelement <4 x float> %538, i64 3
  %865 = fmul contract float %793, %864
  %866 = insertelement <4 x float> %863, float %865, i64 3
  %867 = bitcast <2 x i32> %854 to <4 x bfloat>
  %868 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %827, <4 x bfloat> %867, <4 x float> %866)
  %869 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 5120), i32 %18
  %870 = load i32, ptr addrspace(3) %869, align 4
  %871 = insertelement <2 x i32> poison, i32 %870, i64 0
  %872 = getelementptr inbounds nuw i8, ptr addrspace(3) %869, i32 256
  %873 = load i32, ptr addrspace(3) %872, align 4
  %874 = insertelement <2 x i32> %871, i32 %873, i64 1
  %875 = extractelement <4 x float> %537, i64 0
  %876 = fmul contract float %791, %875
  %877 = insertelement <4 x float> poison, float %876, i64 0
  %878 = extractelement <4 x float> %537, i64 1
  %879 = fmul contract float %793, %878
  %880 = insertelement <4 x float> %877, float %879, i64 1
  %881 = extractelement <4 x float> %537, i64 2
  %882 = fmul contract float %791, %881
  %883 = insertelement <4 x float> %880, float %882, i64 2
  %884 = extractelement <4 x float> %537, i64 3
  %885 = fmul contract float %793, %884
  %886 = insertelement <4 x float> %883, float %885, i64 3
  %887 = bitcast <2 x i32> %874 to <4 x bfloat>
  %888 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %827, <4 x bfloat> %887, <4 x float> %886)
  %889 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 5632), i32 %848
  %890 = load i32, ptr addrspace(3) %889, align 4
  %891 = insertelement <2 x i32> poison, i32 %890, i64 0
  %892 = getelementptr inbounds nuw i8, ptr addrspace(3) %889, i32 256
  %893 = load i32, ptr addrspace(3) %892, align 4
  %894 = insertelement <2 x i32> %891, i32 %893, i64 1
  %895 = extractelement <4 x float> %536, i64 0
  %896 = fmul contract float %791, %895
  %897 = insertelement <4 x float> poison, float %896, i64 0
  %898 = extractelement <4 x float> %536, i64 1
  %899 = fmul contract float %793, %898
  %900 = insertelement <4 x float> %897, float %899, i64 1
  %901 = extractelement <4 x float> %536, i64 2
  %902 = fmul contract float %791, %901
  %903 = insertelement <4 x float> %900, float %902, i64 2
  %904 = extractelement <4 x float> %536, i64 3
  %905 = fmul contract float %793, %904
  %906 = insertelement <4 x float> %903, float %905, i64 3
  %907 = bitcast <2 x i32> %894 to <4 x bfloat>
  %908 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %827, <4 x bfloat> %907, <4 x float> %906)
  %909 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 6144), i32 %18
  %910 = load i32, ptr addrspace(3) %909, align 4
  %911 = insertelement <2 x i32> poison, i32 %910, i64 0
  %912 = getelementptr inbounds nuw i8, ptr addrspace(3) %909, i32 256
  %913 = load i32, ptr addrspace(3) %912, align 4
  %914 = insertelement <2 x i32> %911, i32 %913, i64 1
  %915 = extractelement <4 x float> %535, i64 0
  %916 = fmul contract float %791, %915
  %917 = insertelement <4 x float> poison, float %916, i64 0
  %918 = extractelement <4 x float> %535, i64 1
  %919 = fmul contract float %793, %918
  %920 = insertelement <4 x float> %917, float %919, i64 1
  %921 = extractelement <4 x float> %535, i64 2
  %922 = fmul contract float %791, %921
  %923 = insertelement <4 x float> %920, float %922, i64 2
  %924 = extractelement <4 x float> %535, i64 3
  %925 = fmul contract float %793, %924
  %926 = insertelement <4 x float> %923, float %925, i64 3
  %927 = bitcast <2 x i32> %914 to <4 x bfloat>
  %928 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %827, <4 x bfloat> %927, <4 x float> %926)
  %929 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 6656), i32 %848
  %930 = load i32, ptr addrspace(3) %929, align 4
  %931 = insertelement <2 x i32> poison, i32 %930, i64 0
  %932 = getelementptr inbounds nuw i8, ptr addrspace(3) %929, i32 256
  %933 = load i32, ptr addrspace(3) %932, align 4
  %934 = insertelement <2 x i32> %931, i32 %933, i64 1
  %935 = extractelement <4 x float> %534, i64 0
  %936 = fmul contract float %791, %935
  %937 = insertelement <4 x float> poison, float %936, i64 0
  %938 = extractelement <4 x float> %534, i64 1
  %939 = fmul contract float %793, %938
  %940 = insertelement <4 x float> %937, float %939, i64 1
  %941 = extractelement <4 x float> %534, i64 2
  %942 = fmul contract float %791, %941
  %943 = insertelement <4 x float> %940, float %942, i64 2
  %944 = extractelement <4 x float> %534, i64 3
  %945 = fmul contract float %793, %944
  %946 = insertelement <4 x float> %943, float %945, i64 3
  %947 = bitcast <2 x i32> %934 to <4 x bfloat>
  %948 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %827, <4 x bfloat> %947, <4 x float> %946)
  %949 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 7168), i32 %18
  %950 = load i32, ptr addrspace(3) %949, align 4
  %951 = insertelement <2 x i32> poison, i32 %950, i64 0
  %952 = getelementptr inbounds nuw i8, ptr addrspace(3) %949, i32 256
  %953 = load i32, ptr addrspace(3) %952, align 4
  %954 = insertelement <2 x i32> %951, i32 %953, i64 1
  %955 = extractelement <4 x float> %533, i64 0
  %956 = fmul contract float %791, %955
  %957 = insertelement <4 x float> poison, float %956, i64 0
  %958 = extractelement <4 x float> %533, i64 1
  %959 = fmul contract float %793, %958
  %960 = insertelement <4 x float> %957, float %959, i64 1
  %961 = extractelement <4 x float> %533, i64 2
  %962 = fmul contract float %791, %961
  %963 = insertelement <4 x float> %960, float %962, i64 2
  %964 = extractelement <4 x float> %533, i64 3
  %965 = fmul contract float %793, %964
  %966 = insertelement <4 x float> %963, float %965, i64 3
  %967 = bitcast <2 x i32> %954 to <4 x bfloat>
  %968 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %827, <4 x bfloat> %967, <4 x float> %966)
  %969 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_E5stage, i32 7680), i32 %848
  %970 = load i32, ptr addrspace(3) %969, align 4
  %971 = insertelement <2 x i32> poison, i32 %970, i64 0
  %972 = getelementptr inbounds nuw i8, ptr addrspace(3) %969, i32 256
  %973 = load i32, ptr addrspace(3) %972, align 4
  %974 = insertelement <2 x i32> %971, i32 %973, i64 1
  %975 = extractelement <4 x float> %532, i64 0
  %976 = fmul contract float %791, %975
  %977 = insertelement <4 x float> poison, float %976, i64 0
  %978 = extractelement <4 x float> %532, i64 1
  %979 = fmul contract float %793, %978
  %980 = insertelement <4 x float> %977, float %979, i64 1
  %981 = extractelement <4 x float> %532, i64 2
  %982 = fmul contract float %791, %981
  %983 = insertelement <4 x float> %980, float %982, i64 2
  %984 = extractelement <4 x float> %532, i64 3
  %985 = fmul contract float %793, %984
  %986 = insertelement <4 x float> %983, float %985, i64 3
  %987 = bitcast <2 x i32> %974 to <4 x bfloat>
  %988 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %827, <4 x bfloat> %987, <4 x float> %986)
  tail call void @llvm.bi.sl.barrier()
  br label %989

989:                                              ; preds = %823, %531
  %990 = phi <4 x float> [ %988, %823 ], [ %532, %531 ]
  %991 = phi <4 x float> [ %968, %823 ], [ %533, %531 ]
  %992 = phi <4 x float> [ %948, %823 ], [ %534, %531 ]
  %993 = phi <4 x float> [ %928, %823 ], [ %535, %531 ]
  %994 = phi <4 x float> [ %908, %823 ], [ %536, %531 ]
  %995 = phi <4 x float> [ %888, %823 ], [ %537, %531 ]
  %996 = phi <4 x float> [ %868, %823 ], [ %538, %531 ]
  %997 = phi <4 x float> [ %847, %823 ], [ %539, %531 ]
  %998 = phi float [ %752, %823 ], [ %540, %531 ]
  %999 = phi float [ %753, %823 ], [ %541, %531 ]
  %1000 = phi float [ %794, %823 ], [ %542, %531 ]
  %1001 = phi float [ %795, %823 ], [ %543, %531 ]
  %1002 = or disjoint i32 %22, %35
  %1003 = zext nneg i32 %1002 to i64
  %1004 = or disjoint i64 %1003, 4
  %1005 = mul nsw i64 %9, %24
  %1006 = mul nsw i64 %10, %1003
  %1007 = zext nneg i32 %21 to i64
  %1008 = mul nsw i64 %11, %1007
  %1009 = mul nsw i64 %1004, %10
  %1010 = getelementptr float, ptr addrspace(1) %14, i64 %1005
  %1011 = getelementptr float, ptr addrspace(1) %1010, i64 %1006
  %1012 = getelementptr float, ptr addrspace(1) %1011, i64 %1008
  %1013 = getelementptr float, ptr addrspace(1) %1012, i64 %40
  %1014 = getelementptr float, ptr addrspace(1) %1010, i64 %1009
  %1015 = getelementptr float, ptr addrspace(1) %1014, i64 %1008
  %1016 = getelementptr float, ptr addrspace(1) %1015, i64 %40
  %1017 = extractelement <4 x float> %997, i64 2
  store float %1017, ptr addrspace(1) %1013, align 4
  %1018 = extractelement <4 x float> %997, i64 3
  store float %1018, ptr addrspace(1) %1016, align 4
  %1019 = extractelement <4 x float> %996, i64 2
  %1020 = getelementptr i8, ptr addrspace(1) %1013, i64 64
  store float %1019, ptr addrspace(1) %1020, align 4
  %1021 = extractelement <4 x float> %996, i64 3
  %1022 = getelementptr i8, ptr addrspace(1) %1016, i64 64
  store float %1021, ptr addrspace(1) %1022, align 4
  %1023 = extractelement <4 x float> %995, i64 2
  %1024 = getelementptr i8, ptr addrspace(1) %1013, i64 128
  store float %1023, ptr addrspace(1) %1024, align 4
  %1025 = extractelement <4 x float> %995, i64 3
  %1026 = getelementptr i8, ptr addrspace(1) %1016, i64 128
  store float %1025, ptr addrspace(1) %1026, align 4
  %1027 = extractelement <4 x float> %994, i64 2
  %1028 = getelementptr i8, ptr addrspace(1) %1013, i64 192
  store float %1027, ptr addrspace(1) %1028, align 4
  %1029 = extractelement <4 x float> %994, i64 3
  %1030 = getelementptr i8, ptr addrspace(1) %1016, i64 192
  store float %1029, ptr addrspace(1) %1030, align 4
  %1031 = extractelement <4 x float> %993, i64 2
  %1032 = getelementptr i8, ptr addrspace(1) %1013, i64 256
  store float %1031, ptr addrspace(1) %1032, align 4
  %1033 = extractelement <4 x float> %993, i64 3
  %1034 = getelementptr i8, ptr addrspace(1) %1016, i64 256
  store float %1033, ptr addrspace(1) %1034, align 4
  %1035 = extractelement <4 x float> %992, i64 2
  %1036 = getelementptr i8, ptr addrspace(1) %1013, i64 320
  store float %1035, ptr addrspace(1) %1036, align 4
  %1037 = extractelement <4 x float> %992, i64 3
  %1038 = getelementptr i8, ptr addrspace(1) %1016, i64 320
  store float %1037, ptr addrspace(1) %1038, align 4
  %1039 = extractelement <4 x float> %991, i64 2
  %1040 = getelementptr i8, ptr addrspace(1) %1013, i64 384
  store float %1039, ptr addrspace(1) %1040, align 4
  %1041 = extractelement <4 x float> %991, i64 3
  %1042 = getelementptr i8, ptr addrspace(1) %1016, i64 384
  store float %1041, ptr addrspace(1) %1042, align 4
  %1043 = extractelement <4 x float> %990, i64 2
  %1044 = getelementptr i8, ptr addrspace(1) %1013, i64 448
  store float %1043, ptr addrspace(1) %1044, align 4
  %1045 = extractelement <4 x float> %990, i64 3
  %1046 = getelementptr i8, ptr addrspace(1) %1016, i64 448
  store float %1045, ptr addrspace(1) %1046, align 4
  %1047 = icmp eq i32 %23, 0
  br i1 %1047, label %1048, label %1061

1048:                                             ; preds = %989
  %1049 = mul nsw i64 %12, %24
  %1050 = mul nsw i64 %13, %1003
  %1051 = add i64 %1049, %1007
  %1052 = add i64 %1051, %1050
  %1053 = mul nsw i64 %1004, %13
  %1054 = add i64 %1051, %1053
  %1055 = fmul contract float %998, 0x3FE62E4300000000
  %1056 = getelementptr inbounds float, ptr addrspace(1) %15, i64 %1052
  store float %1055, ptr addrspace(1) %1056, align 4
  %1057 = fmul contract float %999, 0x3FE62E4300000000
  %1058 = getelementptr inbounds float, ptr addrspace(1) %15, i64 %1054
  store float %1057, ptr addrspace(1) %1058, align 4
  %1059 = getelementptr inbounds float, ptr addrspace(1) %16, i64 %1052
  store float %1000, ptr addrspace(1) %1059, align 4
  %1060 = getelementptr inbounds float, ptr addrspace(1) %16, i64 %1054
  store float %1001, ptr addrspace(1) %1060, align 4
  br label %1061

1061:                                             ; preds = %989, %1048, %17
  ret void
}

; Function Attrs: nofree nosync nounwind speculatable memory(none)
declare i32 @llvm.bi.lane.id() #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef range(i32 0, 2147483647) i32 @llvm.nvvm.read.ptx.sreg.ctaid.x() #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef range(i32 0, 65535) i32 @llvm.nvvm.read.ptx.sreg.ctaid.y() #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef range(i32 0, 65535) i32 @llvm.nvvm.read.ptx.sreg.ctaid.z() #2

; Function Attrs: nounwind
declare void @llvm.bi.sl.waitcnt(i64) #3

; Function Attrs: convergent nounwind
declare void @llvm.bi.sl.barrier() #4

; Function Attrs: nounwind memory(argmem: readwrite)
declare void @llvm.bi.sme.load.16x1b64.colxfb16(i32, <4 x i32>, i32, i32) #5

; Function Attrs: nounwind memory(argmem: readwrite)
declare void @llvm.bi.sme.load.16x1b64.rowxfb16(i32, <4 x i32>, i32, i32) #5

; Function Attrs: convergent nofree nounwind memory(none)
declare <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat>, <4 x bfloat>, <4 x float>) #6

; Function Attrs: convergent nofree nounwind memory(none)
declare i32 @llvm.bi.slb.shfl.idx.b32.i32(i32, i32) #6

; Function Attrs: mustprogress nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #7

; Function Attrs: mustprogress nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #7

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(none)
declare float @llvm.nvvm.ex2.approx.f32(float) #8

; Function Attrs: mustprogress nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fma.f32(float, float, float) #7

attributes #0 = { convergent mustprogress norecurse nounwind "frame-pointer"="all" "kernel"="1" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="ivcore11" "target-features"="+async-copy-sme,+mma-i8-mn16k32,+pipe-bar,+v4i8-alu" "uniform-work-group-size"="true" }
attributes #1 = { nofree nosync nounwind speculatable memory(none) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { nounwind }
attributes #4 = { convergent nounwind }
attributes #5 = { nounwind memory(argmem: readwrite) }
attributes #6 = { convergent nofree nounwind memory(none) }
attributes #7 = { mustprogress nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
attributes #8 = { mustprogress nocallback nofree nosync nounwind willreturn memory(none) }

!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 2, !"SDK Version", [2 x i32] [i32 10, i32 2]}
!1 = !{i32 1, !"wchar_size", i32 4}
!2 = !{i32 7, !"frame-pointer", i32 2}
!3 = !{!"clang version 22.1.0git (4.5.0.20260707 a526c4d94919b0feb06f49a88a749e075a7f5cf3)"}
!4 = !{i32 0, i32 64}
!5 = !{}
!6 = !{i32 0, i32 2147483647}
!7 = !{i32 0, i32 65535}
!8 = distinct !{!8, !9}
!9 = !{!"llvm.loop.mustprogress"}
!10 = distinct !{!10, !9}
!11 = distinct !{!11, !9}
