	.text
	.globl	mm_kernel                       ; -- Begin function mm_kernel
	.p2align	3
	.type	mm_kernel,@function
	.iluvatar_kernel mm_kernel
mm_kernel:                              ; @mm_kernel
.Lfunc_begin0:
	.file	1 "/usr/local/lib/python3.12/site-packages/flag_gems/runtime/backend/_iluvatar/ops" "mm.py"
	.loc	1 78 0                          ; mm.py:78:0
	.cfi_sections .debug_frame
	.cfi_startproc
	.cfi_return_column 32
	.iluvatar_kernel_code_t
		iluvatar_code_version_major = 1
		iluvatar_code_version_minor = 3
		iluvatar_machine_kind = 1
		iluvatar_machine_version_major = 1
		iluvatar_machine_version_minor = 1
		iluvatar_machine_version_stepping = 0
		kernel_code_entry_byte_offset = 256
		kernel_code_prefetch_byte_size = 0
		granulated_workitem_vgpr_count = 6
		granulated_warp_sgpr_count = 4
		float_mode = 12
		debug_mode = 0
		has_mbar = 0
		user_sgpr_count = 6
		enable_sgpr_workgroup_id_x = 1
		enable_sgpr_workgroup_id_y = 1
		enable_sgpr_workgroup_id_z = 0
		enable_sgpr_workgroup_info = 1
		enable_vgpr_workitem_id = 3
		granulated_slb_size = 0
		enable_exception = 128
		enable_sgpr_private_segment_buffer = 1
		enable_sgpr_globalvariable_ptr = 0
		enable_sgpr_kernarg_segment_ptr = 1
		enable_sgpr_constvariable_ptr = 0
		enable_sgpr_private_segment_size = 0
		enable_sgpr_grid_workgroup_count_x = 0
		enable_sgpr_grid_workgroup_count_y = 0
		enable_sgpr_grid_workgroup_count_z = 0
		private_element_size = 1
		is_ptr64 = 1
		is_dynamic_callstack = 0
		is_debug_enabled = 0
		enable_private_swizzle = 1
		has_called_assert = 0
		has_called_printf = 0
		has_called_malloc = 0
		enable_srf_flat_shared = 0
		enable_srf_flat_scratch = 0
		has_wgmma = 0
		has_dva = 0
		enable_dynamic_smem_size = 0
		workitem_private_segment_byte_size = 0
		workgroup_group_segment_byte_size = 0
		kernarg_segment_byte_size = 64
		workgroup_fbarrier_count = 0
		warp_sgpr_count = 37
		workitem_vgpr_count = 25
		reserved_vgpr_first = 0
		reserved_vgpr_count = 0
		reserved_sgpr_first = 0
		reserved_sgpr_count = 0
		debug_warp_private_segment_offset_sgpr = 0
		debug_private_segment_buffer_sgpr = 0
		kernarg_segment_alignment = 3
		group_segment_alignment = 4
		private_segment_alignment = 4
		warp_size = 6
		call_convention = -1
		runtime_loader_kernel_symbol = 0
	.end_iluvatar_kernel_code_t
; %bb.0:
	; Func LiveIn Regs:
	;  blockIdx.x : s6  blockIdx.y : s7
	sl_mov_b32 s8, tcr_lo
	ml_vrf_init_u32 v4, tcr
.Ltmp0:
	.file	2 "/usr/local/lib/python3.12/site-packages/triton/language" "standard.py"
	.loc	2 65 17 prologue_end            ; standard.py:65:17 @[ mm.py:114:24 ]
	sl_lsa_load_b32x16 s[12:27], s[4:5], noreg, #0, ca
.Ltmp1:
	.loc	1 121 19                        ; mm.py:121:19
	sl_reg_read s2, hwreg(HW_REG_MODE)
.Ltmp2:
	.loc	2 65 17                         ; standard.py:65:17 @[ mm.py:114:24 ]
	sl_wait smcnt(0)
	sl_add_i32 s0, s19, 0x3f
	.loc	2 65 30 is_stmt 0               ; standard.py:65:30 @[ mm.py:114:24 ]
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_srl_b32 {s1, wcr}, s1, 0x1a
	sl_add_i32 s0, s0, s1
.Ltmp3:
	.loc	1 121 19 is_stmt 1              ; mm.py:121:19
	sl_sra_b32 {s9, wcr}, s0, 0x1f
	sl_sra_b32 {s27, wcr}, s0, 0x6
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_abs_i32 s1, s27
	ml_cvt_f32_u32  v0, s1
	sl_or_b32 {s3, wcr}, s2, 0x3
	ml_rcp_f32 v0, v0
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s3
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s2
	ml_mov_v2s_b32 s4, v0, 0x0
	sl_mov_b32 s26, 0xffffffff
	sl_mul_u64_u32 s[2:3], s4, s1
	sl_neg_i32 s5, s2
	sl_cmp_eq_u32 wcr, s3, 0x0
	sl_csel_b32 s2, s5, s2, wcr
	sl_mul_u64_u32 s[2:3], s2, s4
	sl_add_i32 s2, s4, s3
	sl_sub_i32 s3, s4, s3
	sl_csel_b32 s2, s2, s3, wcr
	sl_mul_u64_u32 s[2:3], s2, s6
	sl_mull_u32 s2, s3, s1
	sl_sub_i32 s4, s6, s2
	sl_cmp_ge_u32 wcr, s4, s1
	sl_sub_bi_u64 s[4:5], s[10:11], s[10:11], wcr
	sl_cmp_ge_u32 wcr, s6, s2
	sl_sub_bi_u32 s1, s10, s10, wcr
	sl_sub_bi_u64 s[24:25], s[10:11], s[10:11], wcr
	sl_and_b64 {s[4:5], wcr}, s[4:5], s[24:25]
	sl_or_b32 {s4, wcr}, s4, s5
	sl_csel_b32 s2, s26, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_add_i32 s2, s3, 0x1
	sl_add_i32 s4, s3, 0xffffffff
	sl_csel_b32 s2, s3, s2, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s2, s4, wcr
	sl_xor_b32 {s1, wcr}, s1, s9
	sl_sub_i32 s1, s1, s9
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s1, 0xffffffff, wcr
	.loc	1 122 18                        ; mm.py:122:18
	sl_mull_u32 s1, s0, s27
	sl_sub_i32 s6, s6, s1
	.loc	1 129 52                        ; mm.py:129:52
	sl_abs_i32 s24, s18
	ml_cvt_f32_u32  v0, s24
	.loc	1 128 21                        ; mm.py:128:21
	sl_mull_u32 s9, s0, 0x40
	.loc	1 129 52                        ; mm.py:129:52
	ml_rcp_f32 v0, v0
	.loc	1 128 44                        ; mm.py:128:44
	sl_and_b32 {s28, wcr}, tcr_lo, 0x300
	.loc	1 129 52                        ; mm.py:129:52
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_sra_b32 {s25, wcr}, s9, 0x1f
	sl_abs_i32 s4, s9
	sl_or_b32 {s1, wcr}, s0, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s0
	ml_mov_v2s_b32 s2, v0, 0x0
	.loc	1 134 21                        ; mm.py:134:21
	sl_mull_u32 s29, s6, 0x40
	.loc	1 129 52                        ; mm.py:129:52
	sl_mul_u64_u32 s[0:1], s2, s24
	sl_neg_i32 s3, s0
	sl_cmp_eq_u32 wcr, s1, 0x0
	sl_csel_b32 s0, s3, s0, wcr
	sl_mul_u64_u32 s[0:1], s0, s2
	sl_add_i32 s0, s2, s1
	sl_sub_i32 s1, s2, s1
	sl_csel_b32 s0, s0, s1, wcr
	sl_mul_u64_u32 s[0:1], s0, s4
	sl_mull_u32 s0, s1, s24
	sl_sub_i32 s1, s4, s0
	sl_cmp_ge_u32 wcr, s1, s24
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	sl_cmp_ge_u32 wcr, s4, s0
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_sub_bi_u64 s[4:5], s[10:11], s[10:11], wcr
	sl_and_b64 {s[2:3], wcr}, s[2:3], s[4:5]
	sl_or_b32 {s2, wcr}, s2, s3
	sl_csel_b32 s2, s26, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_sub_i32 s2, s1, s24
	sl_add_i32 s3, s1, s24
	sl_csel_b32 s1, s1, s2, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s1, s3, wcr
	sl_xor_b32 {s0, wcr}, s0, s25
	.loc	1 135 52                        ; mm.py:135:52
	sl_abs_i32 s24, s19
	ml_cvt_f32_u32  v0, s24
	.loc	1 129 52                        ; mm.py:129:52
	sl_sub_i32 s0, s0, s25
	.loc	1 135 52                        ; mm.py:135:52
	ml_rcp_f32 v0, v0
	.loc	1 129 52                        ; mm.py:129:52
	sl_cmp_ne_u32 wcr, s18, 0x0
	.loc	1 135 52                        ; mm.py:135:52
	sl_reg_read s1, hwreg(HW_REG_MODE)
	.loc	1 129 52                        ; mm.py:129:52
	sl_csel_b32 s25, s0, 0xffffffff, wcr
	.loc	1 135 52                        ; mm.py:135:52
	sl_or_b32 {s0, wcr}, s1, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s0
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_mov_v2s_b32 s2, v0, 0x0
	.loc	1 143 24                        ; mm.py:143:24
	sl_bfe2_b32 s6, tcr_lo, 0x46
	sl_bfe2_b32 s30, tcr_lo, 0x48
	sl_mull_u32 s27, s21, 0x2
	.loc	1 135 52                        ; mm.py:135:52
	sl_mul_u64_u32 s[0:1], s2, s24
	sl_neg_i32 s3, s0
	sl_cmp_eq_u32 wcr, s1, 0x0
	sl_csel_b32 s0, s3, s0, wcr
	sl_mul_u64_u32 s[0:1], s0, s2
	sl_add_i32 s0, s2, s1
	sl_sub_i32 s1, s2, s1
	sl_csel_b32 s0, s0, s1, wcr
	sl_mul_u64_u32 s[0:1], s0, s29
	sl_mull_u32 s0, s1, s24
	sl_sub_i32 s1, s29, s0
	sl_cmp_ge_u32 wcr, s1, s24
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	sl_cmp_ge_u32 wcr, s29, s0
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_sub_bi_u64 s[4:5], s[10:11], s[10:11], wcr
	sl_and_b64 {s[2:3], wcr}, s[2:3], s[4:5]
	sl_or_b32 {s2, wcr}, s2, s3
	sl_csel_b32 s2, s26, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_sub_i32 s2, s1, s24
	sl_add_i32 s3, s1, s24
	sl_csel_b32 s1, s1, s2, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s1, s3, wcr
	sl_cmp_ne_u32 wcr, s19, 0x0
	sl_csel_b32 s2, s0, 0xffffffff, wcr
	.loc	1 136 17                        ; mm.py:136:17
	sl_mull_u32 s3, s7, 0x80
	.loc	1 138 28                        ; mm.py:138:28
	sl_mull_u32 s0, s25, s21
	.loc	1 138 40 is_stmt 0              ; mm.py:138:40
	sl_add_i32 s0, s0, s3
	.loc	1 138 13                        ; mm.py:138:13
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[24:25], s[12:13], s[0:1]
	.loc	1 143 24 is_stmt 1              ; mm.py:143:24
	sl_mull_u32 s0, s6, 0x1000
	sl_mull_u32 s1, s30, 0x400
	sl_add_i32 s12, s0, s1
	sl_mull_u32 s0, s30, 0x40
	sl_mull_u32 s1, s6, s21
	sl_mull_u32 s1, s1, 0x20
	sl_add_i32 s4, s1, s0
	sl_mov_b32 s5, s12
	sl_sme_load_16x1b64_rowxfb16 s[24:27], s[4:5], 0x0, 0x0, 0x0, 0x1
	.loc	1 139 54                        ; mm.py:139:54
	sl_mull_u32 s0, s2, s22
	.loc	1 139 39 is_stmt 0              ; mm.py:139:39
	sl_add_i32 s0, s0, s3
	.loc	1 139 13                        ; mm.py:139:13
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[0:1], s[14:15], s[0:1]
	.loc	1 144 24 is_stmt 1              ; mm.py:144:24
	sl_mull_u32 s3, s22, 0x2
	sl_mov_b32 s2, s26
	sl_mull_u32 s5, s6, 0x400
	sl_mull_u32 s7, s30, 0x1000
	sl_add_i32 s13, s5, s7
	sl_add_i32 s7, s13, 0x8000
	sl_mull_u32 s5, s6, 0x40
	sl_mull_u32 s6, s30, s22
	sl_mull_u32 s6, s6, 0x20
	sl_add_i32 s6, s6, s5
	sl_sme_load_16x1b64_col s[0:3], s[6:7], 0x0, 0x0, 0x0, 0x1
.Ltmp4:
	.loc	2 65 17                         ; standard.py:65:17 @[ mm.py:142:37 ]
	sl_add_i32 s2, s20, 0x7f
.Ltmp5:
	.loc	1 142 26                        ; mm.py:142:26
	sl_cmp_gt_i32 wcr, s2, 0x7f
	sl_mov_b32 s14, 0x0
	.loc	1 140 19                        ; mm.py:140:19
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v2, 0x0
	ml_mov_b32 v3, 0x0
	.loc	1 142 26                        ; mm.py:142:26
	sl_cbr_wcrz BB0_4, wcr
; %bb.1:                                ; %.lr.ph
.Ltmp6:
	.loc	2 65 30                         ; standard.py:65:30 @[ mm.py:142:37 ]
	sl_sra_b32 {s5, wcr}, s2, 0x1f
	sl_srl_b32 {s5, wcr}, s5, 0x19
	sl_add_i32 s2, s2, s5
	sl_sra_b32 {s15, wcr}, s2, 0x7
	sl_mull_u32 s2, s28, 0x10
	ml_shl_b32 v0, v4, 0x2
	ml_and_b32 v0, v0, 0xfc
	ml_add_i32 v5, s2, v0
	ml_shl_b32 v1, v4, 0x6
	sl_mov_b32 s2, 0x3300
	ml_anyop3_b32 v6, s2, v1, v0, 0xfffffff8
	ml_xor_b32 v7, v6, 0x10
	ml_xor_b32 v8, v6, 0x20
	ml_xor_b32 v9, v6, 0x30
.Ltmp7:
	.loc	1 142 26                        ; mm.py:142:26
	sl_add_i64 s[0:1], s[0:1], 0x100
	sl_add_i64 s[24:25], s[24:25], 0x100
	ml_mov_b32 v0, 0x0
	ml_xor_b32 v10, v5, 0x80
	sl_mov_b32 s20, s26
	ml_mov_b32 v1, 0x0
BB0_2:                                  ; =>This Inner Loop Header: Depth=1
	sl_add_i32 s2, s20, 0x1
	sl_cmp_lt_i32 wcr, s2, 0x2
	sl_csel_b32 s20, s2, 0x0, wcr
	.loc	1 143 24                        ; mm.py:143:24
	sl_wait g2scnt(0)
	sl_barrier_req 0x0
	sl_barrier_wait 0x0
	sl_mull_u32 s21, s20, 0x4000
	ml_slb_load_b32x1  v11, v5, s21, #0, null
	sl_add_i32 s22, s21, 0x400
	.loc	1 142 26                        ; mm.py:142:26
	sl_add_i32 s2, s14, 0x1
	sl_cmp_lt_i32 wcr, s2, 0x2
	.loc	1 143 24                        ; mm.py:143:24
	ml_slb_load_b32x1  v12, v5, s21, #256, null
	.loc	1 142 26                        ; mm.py:142:26
	sl_csel_b32 s14, s2, 0x0, wcr
	.loc	1 143 24                        ; mm.py:143:24
	sl_mull_u32 s7, s14, 0x4000
	sl_add_i32 s5, s12, s7
	ml_slb_load_b32x1  v13, v5, s22, #0, null
	sl_sme_load_16x1b64_rowxfb16 s[24:27], s[4:5], 0x0, 0x0, 0x0, 0x1
	sl_add_i32 s5, s21, 0x800
	.loc	1 144 24                        ; mm.py:144:24
	sl_mov_b32 s2, s26
	.loc	1 143 24                        ; mm.py:143:24
	ml_slb_load_b32x1  v14, v5, s22, #256, null
	.loc	1 144 24                        ; mm.py:144:24
	sl_add_i32 s7, s13, s7
	sl_add_i32 s7, s7, 0x8000
	sl_sme_load_16x1b64_col s[0:3], s[6:7], 0x0, 0x0, 0x0, 0x1
	.loc	1 143 24                        ; mm.py:143:24
	ml_slb_load_b32x1  v15, v5, s5, #0, null
	sl_add_i32 s2, s21, 0xc00
	.loc	1 144 24                        ; mm.py:144:24
	sl_add_i32 s7, s21, 0x8000
	sl_add_i32 s30, s21, 0x8400
	.loc	1 143 24                        ; mm.py:143:24
	ml_slb_load_b32x1  v16, v5, s5, #256, null
	.loc	1 144 24                        ; mm.py:144:24
	sl_add_i32 s31, s21, 0x8800
	sl_add_i32 s32, s21, 0x8c00
	.loc	1 142 26                        ; mm.py:142:26
	sl_add_i64 s[0:1], s[0:1], 0x100
	.loc	1 143 24                        ; mm.py:143:24
	ml_slb_load_b32x1  v17, v5, s2, #0, null
	.loc	1 142 26                        ; mm.py:142:26
	sl_add_i32 s15, s15, 0xffffffff
	sl_cmp_eq_u32 wcr, s15, 0x0
	sl_add_i64 s[24:25], s[24:25], 0x100
	.loc	1 143 24                        ; mm.py:143:24
	ml_slb_load_b32x1  v18, v5, s2, #256, null
	ml_slb_load_b32x1  v19, v10, s21, #512, null
	.loc	1 144 24                        ; mm.py:144:24
	ml_slb_load_b32x1  v21, v6, s7, #0, null
	ml_slb_load_b32x1  v22, v7, s7, #0, null
	.loc	1 143 24                        ; mm.py:143:24
	ml_slb_load_b32x1  v20, v10, s21, #768, null
	.loc	1 144 24                        ; mm.py:144:24
	ml_slb_load_b32x1  v23, v8, s7, #0, null
	ml_slb_load_b32x1  v24, v9, s7, #0, null
	.loc	1 150 26                        ; mm.py:150:26
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[11:12], v[21:22], v[0:3]
	.loc	1 143 24                        ; mm.py:143:24
	ml_slb_load_b32x1  v11, v10, s22, #512, null
	.loc	1 144 24                        ; mm.py:144:24
	ml_slb_load_b32x1  v21, v6, s30, #0, null
	ml_slb_load_b32x1  v22, v7, s30, #0, null
	.loc	1 150 26                        ; mm.py:150:26
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[19:20], v[23:24], v[0:3]
	.loc	1 143 24                        ; mm.py:143:24
	ml_slb_load_b32x1  v12, v10, s22, #768, null
	.loc	1 144 24                        ; mm.py:144:24
	ml_slb_load_b32x1  v19, v8, s30, #0, null
	ml_slb_load_b32x1  v20, v9, s30, #0, null
	.loc	1 150 26                        ; mm.py:150:26
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[13:14], v[21:22], v[0:3]
	.loc	1 143 24                        ; mm.py:143:24
	ml_slb_load_b32x1  v13, v10, s5, #512, null
	.loc	1 144 24                        ; mm.py:144:24
	ml_slb_load_b32x1  v21, v6, s31, #0, null
	ml_slb_load_b32x1  v22, v7, s31, #0, null
	.loc	1 150 26                        ; mm.py:150:26
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[11:12], v[19:20], v[0:3]
	.loc	1 143 24                        ; mm.py:143:24
	ml_slb_load_b32x1  v14, v10, s5, #768, null
	.loc	1 144 24                        ; mm.py:144:24
	ml_slb_load_b32x1  v11, v8, s31, #0, null
	ml_slb_load_b32x1  v12, v9, s31, #0, null
	ml_slb_load_b32x1  v19, v6, s32, #0, null
	.loc	1 150 26                        ; mm.py:150:26
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[15:16], v[21:22], v[0:3]
	.loc	1 143 24                        ; mm.py:143:24
	ml_slb_load_b32x1  v15, v10, s2, #512, null
	.loc	1 144 24                        ; mm.py:144:24
	ml_slb_load_b32x1  v20, v7, s32, #0, null
	.loc	1 143 24                        ; mm.py:143:24
	ml_slb_load_b32x1  v16, v10, s2, #768, null
	.loc	1 150 26                        ; mm.py:150:26
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[13:14], v[11:12], v[0:3]
	.loc	1 144 24                        ; mm.py:144:24
	ml_slb_load_b32x1  v11, v8, s32, #0, null
	ml_slb_load_b32x1  v12, v9, s32, #0, null
	.loc	1 150 26                        ; mm.py:150:26
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[17:18], v[19:20], v[0:3]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[15:16], v[11:12], v[0:3]
	.loc	1 142 26                        ; mm.py:142:26
	sl_cbr_wcrz BB0_2, wcr
; %bb.3:                                ; %._crit_edge.loopexit
	.loc	1 188 17                        ; mm.py:188:17
	ml_cvt_bf16_f32  v0, v0
	ml_cvt_bf16_f32  v1, v1
	ml_cvt_bf16_f32  v2, v2
	ml_cvt_bf16_f32  v3, v3
BB0_4:                                  ; %._crit_edge
	.loc	1 128 44                        ; mm.py:128:44
	ml_shl_b32 v7, v4, 0x1
	ml_and_b32 v5, v7, 0xe
	sl_srl_b32 {s0, wcr}, s8, 0x2
	sl_and_b32 {s0, wcr}, s0, 0x30
	.loc	1 134 31                        ; mm.py:134:31
	sl_add_i32 s0, s29, s0
	ml_add_i32 v8, s0, v5
	.loc	1 128 44                        ; mm.py:128:44
	ml_bfe2_b32 v4, v4, 0x63
	sl_srl_b32 {s0, wcr}, s28, 0x4
	.loc	1 128 31 is_stmt 0              ; mm.py:128:31
	sl_add_i32 s0, s9, s0
	ml_add_i32 v9, s0, v4
	ml_add_i32 v10, v9, 0x8
	.loc	1 142 26 is_stmt 1              ; mm.py:142:26
	sl_wait g2scnt(0)
	sl_barrier 
	.loc	1 197 31                        ; mm.py:197:31
	ml_mul_u64_u32 v[4:5], s23, v9
	.loc	1 188 17                        ; mm.py:188:17
	sl_mov_b32 s6, 0x1000504
	sl_mov_b32 s8, 0x2010200
	.loc	1 197 31                        ; mm.py:197:31
	ml_mul_u64_u32 v[5:6], s23, v10
	.loc	1 197 43 is_stmt 0              ; mm.py:197:43
	ml_add_i32 v4, v8, v4
	.loc	1 197 17                        ; mm.py:197:17
	ml_sra_b32 v6, v4, 0x1f
	.loc	1 197 43                        ; mm.py:197:43
	ml_add_i32 v5, v8, v5
	.loc	1 197 17                        ; mm.py:197:17
	ml_shl_b32 v11, v4, 0x1
	ml_shl_b32 v6, v6, 0x1
	ml_addo_u32 {v11, tcr}, s16, v11
	ml_srl_b32 v12, v4, 0x1f
	ml_or_b32 v6, v6, v12
	ml_mov_b32 v12, s17
	ml_addc_i32 v6, v12, v6, tcr
	.loc	1 198 17 is_stmt 1              ; mm.py:198:17
	ml_cmp_gt_i32 tcr, s18, v9
	.loc	1 188 17                        ; mm.py:188:17
	ml_byte_permute_b32 v0, v1, v0, s6
	ml_byte_permute_b32 v1, v3, v2, s6
	ml_and_b32 v2, tid, 0x1
	.loc	1 198 17                        ; mm.py:198:17
	sl_mov_b64 s[0:1], tcr
	ml_cmp_gt_i32 tcr, s18, v10
	ml_mov_b32 v3, 0x5410
	.loc	1 188 17                        ; mm.py:188:17
	ml_bfe2_b32 v10, tid, 0x25
	ml_anyop3_b32 v7, 62, v7, v10, 0xfffffff8
	.loc	1 198 17                        ; mm.py:198:17
	sl_mov_b64 s[2:3], tcr
	.loc	1 198 37 is_stmt 0              ; mm.py:198:37
	ml_cmp_gt_i32 tcr, s19, v8
	.loc	1 201 20 is_stmt 1              ; mm.py:201:20
	ml_sub_i32 v4, v5, v4
	ml_shl_b32 v4, v4, 0x1
	.loc	1 198 37                        ; mm.py:198:37
	sl_mov_b64 s[4:5], tcr
	.loc	1 188 17                        ; mm.py:188:17
	ml_cmp_eq_u32 tcr, v2, 0x0
	ml_mov_b32 v2, 0x7632
	ml_csel_b32 v8, v3, v2, tcr
	ml_csel_b32 v9, v2, v3, tcr
	ml_byte_permute_b32 v8, v8, v8, s8
	ml_pk_shl_b16 v8, v8, 0x40004
	ml_pk_srl_b8 v8, v8, 0x40004
	ml_byte_permute_b32 v8, v0, v1, v8
	ml_byte_permute_b32 v9, v9, v9, s8
	ml_pk_shl_b16 v9, v9, 0x40004
	ml_slb_shuffle_rtn_b32 v8, v8, v7
	ml_pk_srl_b8 v9, v9, 0x40004
	ml_byte_permute_b32 v0, v0, v1, v9
	ml_xor_b32 v1, v7, 0x1
	ml_slb_shuffle_rtn_b32 v0, v0, v1
	.loc	1 198 31                        ; mm.py:198:31
	sl_and_b64 {s[6:7], wcr}, s[0:1], s[4:5]
	sl_and_b64 {s[4:5], wcr}, s[2:3], s[4:5]
	.loc	1 188 17                        ; mm.py:188:17
	ml_and_b32 v1, tid, 0x20
	ml_cmp_eq_u32 tcr, v1, 0x0
	ml_mov_b32 v1, 0x1054
	ml_csel_b32 v1, v3, v1, tcr
	ml_mov_b32 v3, 0x3276
	ml_csel_b32 v2, v2, v3, tcr
	ml_byte_permute_b32 v1, v1, v1, s8
	ml_pk_shl_b16 v1, v1, 0x40004
	ml_pk_srl_b8 v1, v1, 0x40004
	.loc	1 201 20                        ; mm.py:201:20
	ml_mov_v2s_b32 s0, v11, 0x0
	.loc	1 188 17                        ; mm.py:188:17
	ml_byte_permute_b32 v2, v2, v2, s8
	ml_pk_shl_b16 v2, v2, 0x40004
	.loc	1 201 20                        ; mm.py:201:20
	ml_mov_v2s_b32 s1, v6, 0x0
	ml_mov_b32 v3, s0
	ml_sub_i32 v3, v11, v3
	sl_mov_b32 s3, s26
	ml_mov_v2s_b32 s2, v4, 0x0
	.loc	1 188 17                        ; mm.py:188:17
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v1, v8, v0, v1
	.loc	1 201 20                        ; mm.py:201:20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v1, s[0:3], signed v3, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 188 17                        ; mm.py:188:17
	ml_pk_srl_b8 v1, v2, 0x40004
	ml_byte_permute_b32 v0, v8, v0, v1
	.loc	1 201 20                        ; mm.py:201:20
	ml_add_i32 v1, s2, v3
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v0, s[0:3], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 200 4                         ; mm.py:200:4
	sl_eop 
.Ltmp8:
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	mm_kernel.kd
	.type	mm_kernel.kd,@object
	.size	mm_kernel.kd, 64
mm_kernel.kd:
	.asciz	"\000\000\000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	mm_kernel@rel64-mm_kernel.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	536838
	.asciz	"\003\000\264\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	mm_kernel, .Lfunc_end0-mm_kernel
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 2912
; NumSgprs: 37
; NumVgprs: 25
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 4
; VGPRBlocks: 6
; NumSGPRsForWarpsPerNU: 33
; NumVGPRsForWarpsPerNR: 25
; ReqNTIDx: 0
; MaxNTIDx: 0
; MinCTASm: 0
; ActiveWarp: 8
; WarpLimiterHint : 0
	.section	.debug_abbrev,"",@progbits
	.byte	1                               ; Abbreviation Code
	.byte	17                              ; DW_TAG_compile_unit
	.byte	1                               ; DW_CHILDREN_yes
	.byte	37                              ; DW_AT_producer
	.byte	8                               ; DW_FORM_string
	.byte	19                              ; DW_AT_language
	.byte	5                               ; DW_FORM_data2
	.byte	3                               ; DW_AT_name
	.byte	8                               ; DW_FORM_string
	.byte	16                              ; DW_AT_stmt_list
	.byte	6                               ; DW_FORM_data4
	.byte	27                              ; DW_AT_comp_dir
	.byte	8                               ; DW_FORM_string
	.byte	17                              ; DW_AT_low_pc
	.byte	1                               ; DW_FORM_addr
	.byte	18                              ; DW_AT_high_pc
	.byte	1                               ; DW_FORM_addr
	.byte	0                               ; EOM(1)
	.byte	0                               ; EOM(2)
	.byte	2                               ; Abbreviation Code
	.byte	46                              ; DW_TAG_subprogram
	.byte	0                               ; DW_CHILDREN_no
	.byte	3                               ; DW_AT_name
	.byte	8                               ; DW_FORM_string
	.byte	32                              ; DW_AT_inline
	.byte	11                              ; DW_FORM_data1
	.byte	0                               ; EOM(1)
	.byte	0                               ; EOM(2)
	.byte	3                               ; Abbreviation Code
	.byte	46                              ; DW_TAG_subprogram
	.byte	1                               ; DW_CHILDREN_yes
	.byte	17                              ; DW_AT_low_pc
	.byte	1                               ; DW_FORM_addr
	.byte	18                              ; DW_AT_high_pc
	.byte	1                               ; DW_FORM_addr
	.byte	49                              ; DW_AT_abstract_origin
	.byte	19                              ; DW_FORM_ref4
	.byte	0                               ; EOM(1)
	.byte	0                               ; EOM(2)
	.byte	4                               ; Abbreviation Code
	.byte	29                              ; DW_TAG_inlined_subroutine
	.byte	0                               ; DW_CHILDREN_no
	.byte	49                              ; DW_AT_abstract_origin
	.byte	19                              ; DW_FORM_ref4
	.byte	85                              ; DW_AT_ranges
	.byte	6                               ; DW_FORM_data4
	.byte	88                              ; DW_AT_call_file
	.byte	11                              ; DW_FORM_data1
	.byte	89                              ; DW_AT_call_line
	.byte	11                              ; DW_FORM_data1
	.byte	87                              ; DW_AT_call_column
	.byte	11                              ; DW_FORM_data1
	.byte	0                               ; EOM(1)
	.byte	0                               ; EOM(2)
	.byte	0                               ; EOM(3)
	.section	.debug_info,"",@progbits
	.long	182                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0xaf DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"mm.py"                         ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/usr/local/lib/python3.12/site-packages/flag_gems/runtime/backend/_iluvatar/ops" ; DW_AT_comp_dir
	.byte	0
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.byte	2                               ; Abbrev [2] 0x7f:0xc DW_TAG_subprogram
	.ascii	"mm_kernel"                     ; DW_AT_name
	.byte	0
	.byte	1                               ; DW_AT_inline
	.byte	3                               ; Abbrev [3] 0x8b:0x2e DW_TAG_subprogram
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.long	127                             ; DW_AT_abstract_origin
	.byte	4                               ; Abbrev [4] 0xa0:0xc DW_TAG_inlined_subroutine
	.long	127                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges0                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	114                             ; DW_AT_call_line
	.byte	24                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0xac:0xc DW_TAG_inlined_subroutine
	.long	127                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges1                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	142                             ; DW_AT_call_line
	.byte	37                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	0                               ; End Of Children Mark
	.section	.debug_ranges,"",@progbits
.Ldebug_ranges0:
	.quad	.Ltmp0-.Lfunc_begin0
	.quad	.Ltmp1-.Lfunc_begin0
	.quad	.Ltmp2-.Lfunc_begin0
	.quad	.Ltmp3-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges1:
	.quad	.Ltmp4-.Lfunc_begin0
	.quad	.Ltmp5-.Lfunc_begin0
	.quad	.Ltmp6-.Lfunc_begin0
	.quad	.Ltmp7-.Lfunc_begin0
	.quad	0
	.quad	0
	.section	".note.GNU-stack","",@progbits
	.iluvatar_isa "bi-iluvatar-ilurt--ivcore-1-1-0"
	.iluvatar_hsa_metadata
---
iluvatar.kernels:
  - .args:
      - .address_space:  global
        .name:           KArg_0
        .offset:         0
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_1
        .offset:         8
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_2
        .offset:         16
        .size:           8
        .value_kind:     global_buffer
      - .name:           KArg_3
        .offset:         24
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_4
        .offset:         28
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_5
        .offset:         32
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_6
        .offset:         36
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_7
        .offset:         40
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_8
        .offset:         44
        .size:           4
        .value_kind:     by_value
      - .address_space:  global
        .name:           KArg_9
        .offset:         48
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_10
        .offset:         56
        .size:           8
        .value_kind:     global_buffer
    .group_segment_fixed_size: 0
    .kernarg_segment_align: 8
    .kernarg_segment_size: 64
    .max_flat_workgroup_size: 0
    .name:           mm_kernel
    .private_segment_fixed_size: 0
    .sgpr_count:     37
    .sgpr_spill_count: 0
    .symbol:         mm_kernel.kd
    .vgpr_count:     25
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
