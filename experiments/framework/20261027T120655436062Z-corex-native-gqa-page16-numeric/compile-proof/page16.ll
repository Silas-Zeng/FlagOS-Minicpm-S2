; ModuleID = '/workspace/experiments/minicpm-s2/scripts/corex-native-page16-compile-d8364fce/page16.cu'
source_filename = "/workspace/experiments/minicpm-s2/scripts/corex-native-page16-compile-d8364fce/page16.cu"
target datalayout = "e-p:64:64-p1:64:64-p2:32:32-p3:32:32-p4:64:64-p5:32:32-p6:32:32-i64:64-v16:16-v24:32-v32:32-v48:64-v96:128-v192:256-v256:256-v512:512-v1024:1024-v2048:2048-n32:64-S32-A5"
target triple = "bi-iluvatar-ilurt"

%struct.__ix_bfloat16 = type { i16 }

@gSyncThreadsFlag = dso_local local_unnamed_addr addrspace(3) global i32 undef, align 4
@_ZZ19corex_native_page16E5stage = internal addrspace(3) global [2048 x i32] undef, align 16
@gPrintBuf = weak dso_local addrspace(1) externally_initialized global ptr null, align 8
@gAssertReason = weak dso_local addrspace(1) externally_initialized global ptr null, align 8
@llvm.compiler.used = appending global [2 x ptr] [ptr addrspacecast (ptr addrspace(1) @gAssertReason to ptr), ptr addrspacecast (ptr addrspace(1) @gPrintBuf to ptr)], section "llvm.metadata"

; Function Attrs: convergent mustprogress norecurse nounwind
define dso_local iluvatar_kernel void @corex_native_page16(ptr addrspace(1) noundef readonly captures(none) %0, ptr addrspace(1) noundef %1, ptr addrspace(1) noundef %2, ptr addrspace(1) noundef readonly captures(none) %3, float noundef %4, ptr addrspace(1) noundef writeonly captures(none) %5, ptr addrspace(1) noundef writeonly captures(none) %6, ptr addrspace(1) noundef writeonly captures(none) %7, ptr addrspace(1) noundef writeonly captures(none) %8, ptr addrspace(1) noundef writeonly captures(none) %9, ptr addrspace(1) noundef writeonly captures(none) %10, ptr addrspace(1) noundef writeonly captures(none) %11) local_unnamed_addr #0 {
  %13 = tail call i32 @llvm.bi.lane.id(), !range !4, !noundef !5
  %14 = tail call noundef i32 @llvm.nvvm.read.ptx.sreg.ctaid.x(), !range !6
  %15 = lshr i32 %13, 4
  %16 = and i32 %13, 15
  %17 = shl i32 %14, 10
  %18 = shl nuw nsw i32 %15, 8
  %19 = or disjoint i32 %18, %17
  %20 = or disjoint i32 %19, %16
  %21 = zext i32 %20 to i64
  %22 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %21
  %23 = load i16, ptr addrspace(1) %22, align 2
  %24 = or disjoint i32 %20, 128
  %25 = zext i32 %24 to i64
  %26 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %25
  %27 = load i16, ptr addrspace(1) %26, align 2
  %28 = zext i16 %23 to i32
  %29 = zext i16 %27 to i32
  %30 = shl nuw i32 %29, 16
  %31 = or disjoint i32 %30, %28
  %32 = insertelement <2 x i32> poison, i32 %31, i64 0
  %33 = shufflevector <2 x i32> %32, <2 x i32> poison, <2 x i32> zeroinitializer
  %34 = or disjoint i32 %20, 16
  %35 = zext i32 %34 to i64
  %36 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %35
  %37 = load i16, ptr addrspace(1) %36, align 2
  %38 = or disjoint i32 %20, 144
  %39 = zext i32 %38 to i64
  %40 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %39
  %41 = load i16, ptr addrspace(1) %40, align 2
  %42 = zext i16 %37 to i32
  %43 = zext i16 %41 to i32
  %44 = shl nuw i32 %43, 16
  %45 = or disjoint i32 %44, %42
  %46 = insertelement <2 x i32> poison, i32 %45, i64 0
  %47 = shufflevector <2 x i32> %46, <2 x i32> poison, <2 x i32> zeroinitializer
  %48 = or disjoint i32 %20, 32
  %49 = zext i32 %48 to i64
  %50 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %49
  %51 = load i16, ptr addrspace(1) %50, align 2
  %52 = or disjoint i32 %20, 160
  %53 = zext i32 %52 to i64
  %54 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %53
  %55 = load i16, ptr addrspace(1) %54, align 2
  %56 = zext i16 %51 to i32
  %57 = zext i16 %55 to i32
  %58 = shl nuw i32 %57, 16
  %59 = or disjoint i32 %58, %56
  %60 = insertelement <2 x i32> poison, i32 %59, i64 0
  %61 = shufflevector <2 x i32> %60, <2 x i32> poison, <2 x i32> zeroinitializer
  %62 = or disjoint i32 %20, 48
  %63 = zext i32 %62 to i64
  %64 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %63
  %65 = load i16, ptr addrspace(1) %64, align 2
  %66 = or disjoint i32 %20, 176
  %67 = zext i32 %66 to i64
  %68 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %67
  %69 = load i16, ptr addrspace(1) %68, align 2
  %70 = zext i16 %65 to i32
  %71 = zext i16 %69 to i32
  %72 = shl nuw i32 %71, 16
  %73 = or disjoint i32 %72, %70
  %74 = insertelement <2 x i32> poison, i32 %73, i64 0
  %75 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %76 = or disjoint i32 %20, 64
  %77 = zext i32 %76 to i64
  %78 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %77
  %79 = load i16, ptr addrspace(1) %78, align 2
  %80 = or disjoint i32 %20, 192
  %81 = zext i32 %80 to i64
  %82 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %81
  %83 = load i16, ptr addrspace(1) %82, align 2
  %84 = zext i16 %79 to i32
  %85 = zext i16 %83 to i32
  %86 = shl nuw i32 %85, 16
  %87 = or disjoint i32 %86, %84
  %88 = insertelement <2 x i32> poison, i32 %87, i64 0
  %89 = shufflevector <2 x i32> %88, <2 x i32> poison, <2 x i32> zeroinitializer
  %90 = or disjoint i32 %20, 80
  %91 = zext i32 %90 to i64
  %92 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %91
  %93 = load i16, ptr addrspace(1) %92, align 2
  %94 = or disjoint i32 %20, 208
  %95 = zext i32 %94 to i64
  %96 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %95
  %97 = load i16, ptr addrspace(1) %96, align 2
  %98 = zext i16 %93 to i32
  %99 = zext i16 %97 to i32
  %100 = shl nuw i32 %99, 16
  %101 = or disjoint i32 %100, %98
  %102 = insertelement <2 x i32> poison, i32 %101, i64 0
  %103 = shufflevector <2 x i32> %102, <2 x i32> poison, <2 x i32> zeroinitializer
  %104 = or disjoint i32 %20, 96
  %105 = zext i32 %104 to i64
  %106 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %105
  %107 = load i16, ptr addrspace(1) %106, align 2
  %108 = or disjoint i32 %20, 224
  %109 = zext i32 %108 to i64
  %110 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %109
  %111 = load i16, ptr addrspace(1) %110, align 2
  %112 = zext i16 %107 to i32
  %113 = zext i16 %111 to i32
  %114 = shl nuw i32 %113, 16
  %115 = or disjoint i32 %114, %112
  %116 = insertelement <2 x i32> poison, i32 %115, i64 0
  %117 = shufflevector <2 x i32> %116, <2 x i32> poison, <2 x i32> zeroinitializer
  %118 = or disjoint i32 %20, 112
  %119 = zext i32 %118 to i64
  %120 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %119
  %121 = load i16, ptr addrspace(1) %120, align 2
  %122 = or disjoint i32 %20, 240
  %123 = zext i32 %122 to i64
  %124 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %0, i64 %123
  %125 = load i16, ptr addrspace(1) %124, align 2
  %126 = zext i16 %121 to i32
  %127 = zext i16 %125 to i32
  %128 = shl nuw i32 %127, 16
  %129 = or disjoint i32 %128, %126
  %130 = insertelement <2 x i32> poison, i32 %129, i64 0
  %131 = shufflevector <2 x i32> %130, <2 x i32> poison, <2 x i32> zeroinitializer
  %132 = load i32, ptr addrspace(1) %3, align 4
  %133 = sext i32 %132 to i64
  %134 = shl nsw i64 %133, 14
  %135 = getelementptr inbounds i8, ptr addrspace(1) %1, i64 %134
  %136 = addrspacecast ptr addrspace(1) %135 to ptr
  %137 = shl i32 %14, 7
  %138 = zext i32 %137 to i64
  %139 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr %136, i64 %138
  %140 = ptrtoint ptr %139 to i64
  %141 = insertelement <2 x i64> poison, i64 %140, i64 0
  %142 = bitcast <2 x i64> %141 to <4 x i32>
  %143 = shufflevector <4 x i32> %142, <4 x i32> <i32 poison, i32 poison, i32 -1, i32 512>, <4 x i32> <i32 0, i32 1, i32 6, i32 7>
  %144 = getelementptr inbounds i8, ptr addrspace(1) %2, i64 %134
  %145 = addrspacecast ptr addrspace(1) %144 to ptr
  %146 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr %145, i64 %138
  %147 = ptrtoint ptr %146 to i64
  %148 = insertelement <2 x i64> poison, i64 %147, i64 0
  %149 = bitcast <2 x i64> %148 to <4 x i32>
  %150 = shufflevector <4 x i32> %149, <4 x i32> <i32 poison, i32 poison, i32 -1, i32 512>, <4 x i32> <i32 0, i32 1, i32 6, i32 7>
  tail call void @llvm.bi.sme.load.16x1b64.colxfb16(i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ19corex_native_page16E5stage to ptr) to i32), <4 x i32> %143, i32 0, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.colxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ19corex_native_page16E5stage to ptr) to i32), i32 1024), <4 x i32> %143, i32 64, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.colxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ19corex_native_page16E5stage to ptr) to i32), i32 2048), <4 x i32> %143, i32 128, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.colxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ19corex_native_page16E5stage to ptr) to i32), i32 3072), <4 x i32> %143, i32 192, i32 0)
  tail call void @llvm.bi.sl.waitcnt(i64 8)
  tail call void @llvm.bi.sme.load.16x1b64.rowxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ19corex_native_page16E5stage to ptr) to i32), i32 4096), <4 x i32> %150, i32 0, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.rowxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ19corex_native_page16E5stage to ptr) to i32), i32 5120), <4 x i32> %150, i32 64, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.rowxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ19corex_native_page16E5stage to ptr) to i32), i32 6144), <4 x i32> %150, i32 128, i32 0)
  tail call void @llvm.bi.sme.load.16x1b64.rowxfb16(i32 add (i32 ptrtoint (ptr addrspacecast (ptr addrspace(3) @_ZZ19corex_native_page16E5stage to ptr) to i32), i32 7168), <4 x i32> %150, i32 192, i32 0)
  tail call void @llvm.bi.sl.waitcnt(i64 8)
  tail call void @llvm.bi.sl.barrier()
  %151 = shl i32 %14, 11
  br label %324

152:                                              ; preds = %324
  %153 = shl nuw nsw i32 %13, 4
  %154 = and i32 %153, 192
  %155 = getelementptr inbounds nuw i32, ptr addrspace(3) @_ZZ19corex_native_page16E5stage, i32 %154
  %156 = getelementptr inbounds nuw i32, ptr addrspace(3) %155, i32 %13
  %157 = load i32, ptr addrspace(3) %156, align 4
  %158 = insertelement <2 x i32> poison, i32 %157, i64 0
  %159 = xor i32 %13, 4
  %160 = getelementptr inbounds nuw i32, ptr addrspace(3) %155, i32 %159
  %161 = load i32, ptr addrspace(3) %160, align 4
  %162 = insertelement <2 x i32> %158, i32 %161, i64 1
  %163 = bitcast <2 x i32> %33 to <4 x bfloat>
  %164 = bitcast <2 x i32> %162 to <4 x bfloat>
  %165 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %163, <4 x bfloat> %164, <4 x float> zeroinitializer)
  %166 = xor i32 %13, 8
  %167 = getelementptr inbounds nuw i32, ptr addrspace(3) %155, i32 %166
  %168 = load i32, ptr addrspace(3) %167, align 4
  %169 = insertelement <2 x i32> poison, i32 %168, i64 0
  %170 = xor i32 %13, 12
  %171 = getelementptr inbounds nuw i32, ptr addrspace(3) %155, i32 %170
  %172 = load i32, ptr addrspace(3) %171, align 4
  %173 = insertelement <2 x i32> %169, i32 %172, i64 1
  %174 = bitcast <2 x i32> %47 to <4 x bfloat>
  %175 = bitcast <2 x i32> %173 to <4 x bfloat>
  %176 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %174, <4 x bfloat> %175, <4 x float> %165)
  %177 = getelementptr inbounds nuw i8, ptr addrspace(3) %155, i32 1024
  %178 = getelementptr inbounds nuw i32, ptr addrspace(3) %177, i32 %13
  %179 = load i32, ptr addrspace(3) %178, align 4
  %180 = insertelement <2 x i32> poison, i32 %179, i64 0
  %181 = getelementptr inbounds nuw i32, ptr addrspace(3) %177, i32 %159
  %182 = load i32, ptr addrspace(3) %181, align 4
  %183 = insertelement <2 x i32> %180, i32 %182, i64 1
  %184 = bitcast <2 x i32> %61 to <4 x bfloat>
  %185 = bitcast <2 x i32> %183 to <4 x bfloat>
  %186 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %184, <4 x bfloat> %185, <4 x float> %176)
  %187 = getelementptr inbounds nuw i32, ptr addrspace(3) %177, i32 %166
  %188 = load i32, ptr addrspace(3) %187, align 4
  %189 = insertelement <2 x i32> poison, i32 %188, i64 0
  %190 = getelementptr inbounds nuw i32, ptr addrspace(3) %177, i32 %170
  %191 = load i32, ptr addrspace(3) %190, align 4
  %192 = insertelement <2 x i32> %189, i32 %191, i64 1
  %193 = bitcast <2 x i32> %75 to <4 x bfloat>
  %194 = bitcast <2 x i32> %192 to <4 x bfloat>
  %195 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %193, <4 x bfloat> %194, <4 x float> %186)
  %196 = getelementptr inbounds nuw i8, ptr addrspace(3) %155, i32 2048
  %197 = getelementptr inbounds nuw i32, ptr addrspace(3) %196, i32 %13
  %198 = load i32, ptr addrspace(3) %197, align 4
  %199 = insertelement <2 x i32> poison, i32 %198, i64 0
  %200 = getelementptr inbounds nuw i32, ptr addrspace(3) %196, i32 %159
  %201 = load i32, ptr addrspace(3) %200, align 4
  %202 = insertelement <2 x i32> %199, i32 %201, i64 1
  %203 = bitcast <2 x i32> %89 to <4 x bfloat>
  %204 = bitcast <2 x i32> %202 to <4 x bfloat>
  %205 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %203, <4 x bfloat> %204, <4 x float> %195)
  %206 = getelementptr inbounds nuw i32, ptr addrspace(3) %196, i32 %166
  %207 = load i32, ptr addrspace(3) %206, align 4
  %208 = insertelement <2 x i32> poison, i32 %207, i64 0
  %209 = getelementptr inbounds nuw i32, ptr addrspace(3) %196, i32 %170
  %210 = load i32, ptr addrspace(3) %209, align 4
  %211 = insertelement <2 x i32> %208, i32 %210, i64 1
  %212 = bitcast <2 x i32> %103 to <4 x bfloat>
  %213 = bitcast <2 x i32> %211 to <4 x bfloat>
  %214 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %212, <4 x bfloat> %213, <4 x float> %205)
  %215 = getelementptr inbounds nuw i8, ptr addrspace(3) %155, i32 3072
  %216 = getelementptr inbounds nuw i32, ptr addrspace(3) %215, i32 %13
  %217 = load i32, ptr addrspace(3) %216, align 4
  %218 = insertelement <2 x i32> poison, i32 %217, i64 0
  %219 = getelementptr inbounds nuw i32, ptr addrspace(3) %215, i32 %159
  %220 = load i32, ptr addrspace(3) %219, align 4
  %221 = insertelement <2 x i32> %218, i32 %220, i64 1
  %222 = bitcast <2 x i32> %117 to <4 x bfloat>
  %223 = bitcast <2 x i32> %221 to <4 x bfloat>
  %224 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %222, <4 x bfloat> %223, <4 x float> %214)
  %225 = getelementptr inbounds nuw i32, ptr addrspace(3) %215, i32 %166
  %226 = load i32, ptr addrspace(3) %225, align 4
  %227 = insertelement <2 x i32> poison, i32 %226, i64 0
  %228 = getelementptr inbounds nuw i32, ptr addrspace(3) %215, i32 %170
  %229 = load i32, ptr addrspace(3) %228, align 4
  %230 = insertelement <2 x i32> %227, i32 %229, i64 1
  %231 = bitcast <2 x i32> %131 to <4 x bfloat>
  %232 = bitcast <2 x i32> %230 to <4 x bfloat>
  %233 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %231, <4 x bfloat> %232, <4 x float> %224)
  %234 = extractelement <4 x float> %233, i64 0
  %235 = fmul contract float %4, %234
  %236 = extractelement <4 x float> %233, i64 1
  %237 = fmul contract float %4, %236
  %238 = bitcast float %235 to i32
  %239 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %238, i32 %166)
  %240 = bitcast i32 %239 to float
  %241 = tail call noundef float @llvm.maxnum.f32(float %235, float %240)
  %242 = bitcast float %237 to i32
  %243 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %242, i32 %166)
  %244 = bitcast i32 %243 to float
  %245 = tail call noundef float @llvm.maxnum.f32(float %237, float %244)
  %246 = bitcast float %241 to i32
  %247 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %246, i32 %159)
  %248 = bitcast i32 %247 to float
  %249 = tail call noundef float @llvm.maxnum.f32(float %241, float %248)
  %250 = bitcast float %245 to i32
  %251 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %250, i32 %159)
  %252 = bitcast i32 %251 to float
  %253 = tail call noundef float @llvm.maxnum.f32(float %245, float %252)
  %254 = xor i32 %13, 2
  %255 = bitcast float %249 to i32
  %256 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %255, i32 %254)
  %257 = bitcast i32 %256 to float
  %258 = tail call noundef float @llvm.maxnum.f32(float %249, float %257)
  %259 = bitcast float %253 to i32
  %260 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %259, i32 %254)
  %261 = bitcast i32 %260 to float
  %262 = tail call noundef float @llvm.maxnum.f32(float %253, float %261)
  %263 = xor i32 %13, 1
  %264 = bitcast float %258 to i32
  %265 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %264, i32 %263)
  %266 = bitcast i32 %265 to float
  %267 = tail call noundef float @llvm.maxnum.f32(float %258, float %266)
  %268 = bitcast float %262 to i32
  %269 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %268, i32 %263)
  %270 = bitcast i32 %269 to float
  %271 = tail call noundef float @llvm.maxnum.f32(float %262, float %270)
  %272 = fsub contract float %235, %267
  %273 = tail call noundef float @llvm.nvvm.ex2.approx.f32(float %272)
  %274 = fsub contract float %237, %271
  %275 = tail call noundef float @llvm.nvvm.ex2.approx.f32(float %274)
  %276 = bitcast float %273 to i32
  %277 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %276, i32 %166)
  %278 = bitcast i32 %277 to float
  %279 = fadd contract float %273, %278
  %280 = bitcast float %275 to i32
  %281 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %280, i32 %166)
  %282 = bitcast i32 %281 to float
  %283 = fadd contract float %275, %282
  %284 = bitcast float %279 to i32
  %285 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %284, i32 %159)
  %286 = bitcast i32 %285 to float
  %287 = fadd contract float %279, %286
  %288 = bitcast float %283 to i32
  %289 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %288, i32 %159)
  %290 = bitcast i32 %289 to float
  %291 = fadd contract float %283, %290
  %292 = bitcast float %287 to i32
  %293 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %292, i32 %254)
  %294 = bitcast i32 %293 to float
  %295 = fadd contract float %287, %294
  %296 = bitcast float %291 to i32
  %297 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %296, i32 %254)
  %298 = bitcast i32 %297 to float
  %299 = fadd contract float %291, %298
  %300 = bitcast float %295 to i32
  %301 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %300, i32 %263)
  %302 = bitcast float %299 to i32
  %303 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 %302, i32 %263)
  %304 = fptrunc contract float %273 to bfloat
  %305 = bitcast bfloat %304 to i16
  %306 = fptrunc contract float %275 to bfloat
  %307 = bitcast bfloat %306 to i16
  %308 = shl i32 %14, 3
  %309 = or disjoint i32 %15, %308
  %310 = or disjoint i32 %309, 4
  %311 = shl i32 %309, 4
  %312 = or disjoint i32 %311, %16
  %313 = zext i32 %312 to i64
  %314 = getelementptr inbounds nuw float, ptr addrspace(1) %8, i64 %313
  store float %235, ptr addrspace(1) %314, align 4
  %315 = shl i32 %310, 4
  %316 = or disjoint i32 %315, %16
  %317 = zext i32 %316 to i64
  %318 = getelementptr inbounds nuw float, ptr addrspace(1) %8, i64 %317
  store float %237, ptr addrspace(1) %318, align 4
  %319 = getelementptr inbounds nuw float, ptr addrspace(1) %9, i64 %313
  store float %273, ptr addrspace(1) %319, align 4
  %320 = getelementptr inbounds nuw float, ptr addrspace(1) %9, i64 %317
  store float %275, ptr addrspace(1) %320, align 4
  %321 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %10, i64 %313
  store bfloat %304, ptr addrspace(1) %321, align 2
  %322 = getelementptr inbounds nuw %struct.__ix_bfloat16, ptr addrspace(1) %10, i64 %317
  store bfloat %306, ptr addrspace(1) %322, align 2
  %323 = icmp eq i32 %16, 0
  br i1 %323, label %333, label %346

324:                                              ; preds = %12, %324
  %325 = phi i32 [ %13, %12 ], [ %331, %324 ]
  %326 = getelementptr inbounds nuw i32, ptr addrspace(3) @_ZZ19corex_native_page16E5stage, i32 %325
  %327 = load i32, ptr addrspace(3) %326, align 4
  %328 = add nuw nsw i32 %325, %151
  %329 = zext i32 %328 to i64
  %330 = getelementptr inbounds nuw i32, ptr addrspace(1) %11, i64 %329
  store i32 %327, ptr addrspace(1) %330, align 4
  %331 = add nuw nsw i32 %325, 64
  %332 = icmp samesign ult i32 %325, 1984
  br i1 %332, label %324, label %152, !llvm.loop !7

333:                                              ; preds = %152
  %334 = bitcast i32 %303 to float
  %335 = fadd contract float %299, %334
  %336 = bitcast i32 %301 to float
  %337 = fadd contract float %295, %336
  %338 = zext i32 %310 to i64
  %339 = getelementptr inbounds nuw float, ptr addrspace(1) %7, i64 %338
  %340 = zext i32 %309 to i64
  %341 = getelementptr inbounds nuw float, ptr addrspace(1) %7, i64 %340
  %342 = getelementptr inbounds nuw float, ptr addrspace(1) %6, i64 %338
  %343 = fmul contract float %271, 0x3FE62E4300000000
  %344 = getelementptr inbounds nuw float, ptr addrspace(1) %6, i64 %340
  %345 = fmul contract float %267, 0x3FE62E4300000000
  store float %345, ptr addrspace(1) %344, align 4
  store float %343, ptr addrspace(1) %342, align 4
  store float %337, ptr addrspace(1) %341, align 4
  store float %335, ptr addrspace(1) %339, align 4
  br label %346

346:                                              ; preds = %333, %152
  %347 = and i32 %13, 16
  %348 = icmp eq i32 %347, 0
  %349 = select i1 %348, i16 %305, i16 %307
  %350 = zext i16 %349 to i32
  %351 = select i1 %348, i16 %307, i16 %305
  %352 = zext i16 %351 to i32
  %353 = shl nuw nsw i32 %347, 1
  %354 = and i32 %13, 32
  %355 = lshr exact i32 %354, 1
  %356 = or disjoint i32 %353, %355
  %357 = or disjoint i32 %356, %16
  %358 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 range(i32 0, 65536) %350, i32 range(i32 0, 64) %357)
  %359 = xor i32 %357, 16
  %360 = tail call noundef i32 @llvm.bi.slb.shfl.idx.b32.i32(i32 range(i32 0, 65536) %352, i32 range(i32 0, 64) %359)
  %361 = icmp eq i32 %354, 0
  br i1 %361, label %366, label %362

362:                                              ; preds = %346
  %363 = and i32 %360, 65535
  %364 = shl i32 %358, 16
  %365 = or disjoint i32 %363, %364
  br label %370

366:                                              ; preds = %346
  %367 = and i32 %358, 65535
  %368 = shl i32 %360, 16
  %369 = or disjoint i32 %368, %367
  br label %370

370:                                              ; preds = %366, %362
  %371 = phi i32 [ %365, %362 ], [ %369, %366 ]
  %372 = insertelement <2 x i32> poison, i32 %371, i64 0
  %373 = shufflevector <2 x i32> %372, <2 x i32> poison, <2 x i32> zeroinitializer
  %374 = bitcast <2 x i32> %373 to <4 x bfloat>
  %375 = shl i32 %309, 7
  %376 = or disjoint i32 %375, %16
  %377 = shl i32 %310, 7
  %378 = or disjoint i32 %377, %16
  %379 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ19corex_native_page16E5stage, i32 4096), i32 %13
  %380 = load i32, ptr addrspace(3) %379, align 4
  %381 = insertelement <2 x i32> poison, i32 %380, i64 0
  %382 = getelementptr inbounds nuw i8, ptr addrspace(3) %379, i32 256
  %383 = load i32, ptr addrspace(3) %382, align 4
  %384 = insertelement <2 x i32> %381, i32 %383, i64 1
  %385 = bitcast <2 x i32> %384 to <4 x bfloat>
  %386 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %374, <4 x bfloat> %385, <4 x float> zeroinitializer)
  %387 = extractelement <4 x float> %386, i64 2
  %388 = zext i32 %376 to i64
  %389 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %388
  store float %387, ptr addrspace(1) %389, align 4
  %390 = extractelement <4 x float> %386, i64 3
  %391 = zext i32 %378 to i64
  %392 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %391
  store float %390, ptr addrspace(1) %392, align 4
  %393 = xor i32 %13, 32
  %394 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ19corex_native_page16E5stage, i32 4608), i32 %393
  %395 = load i32, ptr addrspace(3) %394, align 4
  %396 = insertelement <2 x i32> poison, i32 %395, i64 0
  %397 = getelementptr inbounds nuw i8, ptr addrspace(3) %394, i32 256
  %398 = load i32, ptr addrspace(3) %397, align 4
  %399 = insertelement <2 x i32> %396, i32 %398, i64 1
  %400 = bitcast <2 x i32> %399 to <4 x bfloat>
  %401 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %374, <4 x bfloat> %400, <4 x float> zeroinitializer)
  %402 = extractelement <4 x float> %401, i64 2
  %403 = or disjoint i32 %376, 16
  %404 = zext i32 %403 to i64
  %405 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %404
  store float %402, ptr addrspace(1) %405, align 4
  %406 = extractelement <4 x float> %401, i64 3
  %407 = or disjoint i32 %378, 16
  %408 = zext i32 %407 to i64
  %409 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %408
  store float %406, ptr addrspace(1) %409, align 4
  %410 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ19corex_native_page16E5stage, i32 5120), i32 %13
  %411 = load i32, ptr addrspace(3) %410, align 4
  %412 = insertelement <2 x i32> poison, i32 %411, i64 0
  %413 = getelementptr inbounds nuw i8, ptr addrspace(3) %410, i32 256
  %414 = load i32, ptr addrspace(3) %413, align 4
  %415 = insertelement <2 x i32> %412, i32 %414, i64 1
  %416 = bitcast <2 x i32> %415 to <4 x bfloat>
  %417 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %374, <4 x bfloat> %416, <4 x float> zeroinitializer)
  %418 = extractelement <4 x float> %417, i64 2
  %419 = or disjoint i32 %376, 32
  %420 = zext i32 %419 to i64
  %421 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %420
  store float %418, ptr addrspace(1) %421, align 4
  %422 = extractelement <4 x float> %417, i64 3
  %423 = or disjoint i32 %378, 32
  %424 = zext i32 %423 to i64
  %425 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %424
  store float %422, ptr addrspace(1) %425, align 4
  %426 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ19corex_native_page16E5stage, i32 5632), i32 %393
  %427 = load i32, ptr addrspace(3) %426, align 4
  %428 = insertelement <2 x i32> poison, i32 %427, i64 0
  %429 = getelementptr inbounds nuw i8, ptr addrspace(3) %426, i32 256
  %430 = load i32, ptr addrspace(3) %429, align 4
  %431 = insertelement <2 x i32> %428, i32 %430, i64 1
  %432 = bitcast <2 x i32> %431 to <4 x bfloat>
  %433 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %374, <4 x bfloat> %432, <4 x float> zeroinitializer)
  %434 = extractelement <4 x float> %433, i64 2
  %435 = or disjoint i32 %376, 48
  %436 = zext i32 %435 to i64
  %437 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %436
  store float %434, ptr addrspace(1) %437, align 4
  %438 = extractelement <4 x float> %433, i64 3
  %439 = or disjoint i32 %378, 48
  %440 = zext i32 %439 to i64
  %441 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %440
  store float %438, ptr addrspace(1) %441, align 4
  %442 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ19corex_native_page16E5stage, i32 6144), i32 %13
  %443 = load i32, ptr addrspace(3) %442, align 4
  %444 = insertelement <2 x i32> poison, i32 %443, i64 0
  %445 = getelementptr inbounds nuw i8, ptr addrspace(3) %442, i32 256
  %446 = load i32, ptr addrspace(3) %445, align 4
  %447 = insertelement <2 x i32> %444, i32 %446, i64 1
  %448 = bitcast <2 x i32> %447 to <4 x bfloat>
  %449 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %374, <4 x bfloat> %448, <4 x float> zeroinitializer)
  %450 = extractelement <4 x float> %449, i64 2
  %451 = or disjoint i32 %376, 64
  %452 = zext i32 %451 to i64
  %453 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %452
  store float %450, ptr addrspace(1) %453, align 4
  %454 = extractelement <4 x float> %449, i64 3
  %455 = or disjoint i32 %378, 64
  %456 = zext i32 %455 to i64
  %457 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %456
  store float %454, ptr addrspace(1) %457, align 4
  %458 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ19corex_native_page16E5stage, i32 6656), i32 %393
  %459 = load i32, ptr addrspace(3) %458, align 4
  %460 = insertelement <2 x i32> poison, i32 %459, i64 0
  %461 = getelementptr inbounds nuw i8, ptr addrspace(3) %458, i32 256
  %462 = load i32, ptr addrspace(3) %461, align 4
  %463 = insertelement <2 x i32> %460, i32 %462, i64 1
  %464 = bitcast <2 x i32> %463 to <4 x bfloat>
  %465 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %374, <4 x bfloat> %464, <4 x float> zeroinitializer)
  %466 = extractelement <4 x float> %465, i64 2
  %467 = or disjoint i32 %376, 80
  %468 = zext i32 %467 to i64
  %469 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %468
  store float %466, ptr addrspace(1) %469, align 4
  %470 = extractelement <4 x float> %465, i64 3
  %471 = or disjoint i32 %378, 80
  %472 = zext i32 %471 to i64
  %473 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %472
  store float %470, ptr addrspace(1) %473, align 4
  %474 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ19corex_native_page16E5stage, i32 7168), i32 %13
  %475 = load i32, ptr addrspace(3) %474, align 4
  %476 = insertelement <2 x i32> poison, i32 %475, i64 0
  %477 = getelementptr inbounds nuw i8, ptr addrspace(3) %474, i32 256
  %478 = load i32, ptr addrspace(3) %477, align 4
  %479 = insertelement <2 x i32> %476, i32 %478, i64 1
  %480 = bitcast <2 x i32> %479 to <4 x bfloat>
  %481 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %374, <4 x bfloat> %480, <4 x float> zeroinitializer)
  %482 = extractelement <4 x float> %481, i64 2
  %483 = or disjoint i32 %376, 96
  %484 = zext i32 %483 to i64
  %485 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %484
  store float %482, ptr addrspace(1) %485, align 4
  %486 = extractelement <4 x float> %481, i64 3
  %487 = or disjoint i32 %378, 96
  %488 = zext i32 %487 to i64
  %489 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %488
  store float %486, ptr addrspace(1) %489, align 4
  %490 = getelementptr inbounds nuw i32, ptr addrspace(3) getelementptr inbounds nuw (i8, ptr addrspace(3) @_ZZ19corex_native_page16E5stage, i32 7680), i32 %393
  %491 = load i32, ptr addrspace(3) %490, align 4
  %492 = insertelement <2 x i32> poison, i32 %491, i64 0
  %493 = getelementptr inbounds nuw i8, ptr addrspace(3) %490, i32 256
  %494 = load i32, ptr addrspace(3) %493, align 4
  %495 = insertelement <2 x i32> %492, i32 %494, i64 1
  %496 = bitcast <2 x i32> %495 to <4 x bfloat>
  %497 = tail call contract <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat> %374, <4 x bfloat> %496, <4 x float> zeroinitializer)
  %498 = extractelement <4 x float> %497, i64 2
  %499 = or disjoint i32 %376, 112
  %500 = zext i32 %499 to i64
  %501 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %500
  store float %498, ptr addrspace(1) %501, align 4
  %502 = extractelement <4 x float> %497, i64 3
  %503 = or disjoint i32 %378, 112
  %504 = zext i32 %503 to i64
  %505 = getelementptr inbounds nuw float, ptr addrspace(1) %5, i64 %504
  store float %502, ptr addrspace(1) %505, align 4
  ret void
}

; Function Attrs: nofree nosync nounwind speculatable memory(none)
declare i32 @llvm.bi.lane.id() #1

; Function Attrs: nounwind memory(argmem: readwrite)
declare void @llvm.bi.sme.load.16x1b64.colxfb16(i32, <4 x i32>, i32, i32) #2

; Function Attrs: nounwind
declare void @llvm.bi.sl.waitcnt(i64) #3

; Function Attrs: nounwind memory(argmem: readwrite)
declare void @llvm.bi.sme.load.16x1b64.rowxfb16(i32, <4 x i32>, i32, i32) #2

; Function Attrs: convergent nounwind
declare void @llvm.bi.sl.barrier() #4

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef range(i32 0, 2147483647) i32 @llvm.nvvm.read.ptx.sreg.ctaid.x() #5

; Function Attrs: convergent nofree nounwind memory(none)
declare i32 @llvm.bi.slb.shfl.idx.b32.i32(i32, i32) #6

; Function Attrs: convergent nofree nounwind memory(none)
declare <4 x float> @llvm.bi.matrix.mad.f32x4.bf16x4(<4 x bfloat>, <4 x bfloat>, <4 x float>) #6

; Function Attrs: mustprogress nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #7

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(none)
declare float @llvm.nvvm.ex2.approx.f32(float) #8

attributes #0 = { convergent mustprogress norecurse nounwind "frame-pointer"="all" "kernel"="1" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="ivcore11" "target-features"="+async-copy-sme,+mma-i8-mn16k32,+pipe-bar,+v4i8-alu" "uniform-work-group-size"="true" }
attributes #1 = { nofree nosync nounwind speculatable memory(none) }
attributes #2 = { nounwind memory(argmem: readwrite) }
attributes #3 = { nounwind }
attributes #4 = { convergent nounwind }
attributes #5 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
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
!7 = distinct !{!7, !8}
!8 = !{!"llvm.loop.mustprogress"}
