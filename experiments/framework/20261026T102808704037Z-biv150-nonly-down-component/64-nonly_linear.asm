	.text
	.globl	nonly_linear                    ; -- Begin function nonly_linear
	.p2align	3
	.type	nonly_linear,@function
	.iluvatar_kernel nonly_linear
nonly_linear:                           ; @nonly_linear
.Lfunc_begin0:
	.file	1 "/workspace/experiments/minicpm-s2/framework/20261026T102808704037Z-biv150-nonly-down-component/source" "candidate.py"
	.loc	1 27 0                          ; candidate.py:27:0
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
		granulated_warp_sgpr_count = 5
		float_mode = 12
		debug_mode = 0
		has_mbar = 0
		user_sgpr_count = 6
		enable_sgpr_workgroup_id_x = 1
		enable_sgpr_workgroup_id_y = 0
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
		warp_sgpr_count = 42
		workitem_vgpr_count = 28
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
	;  blockIdx.x : s6
	sl_mov_b32 s10, tcr_lo
	ml_vrf_init_u32 v16, tcr
.Ltmp0:
	.file	2 "/usr/local/lib/python3.12/site-packages/triton/language" "standard.py"
	.loc	2 65 17 prologue_end            ; standard.py:65:17 @[ candidate.py:29:42 ]
	sl_lsa_load_b32x16 s[12:27], s[4:5], noreg, #0, ca
.Ltmp1:
	.loc	2 65 17 is_stmt 0               ; standard.py:65:17 @[ candidate.py:29:21 ]
	sl_wait smcnt(0)
	sl_add_i32 s0, s18, 0x3f
.Ltmp2:
	.loc	2 65 17                         ; standard.py:65:17 @[ candidate.py:29:42 ]
	sl_add_i32 s1, s19, 0x7f
.Ltmp3:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:29:21 ]
	sl_sra_b32 {s2, wcr}, s0, 0x1f
.Ltmp4:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:29:42 ]
	sl_sra_b32 {s3, wcr}, s1, 0x1f
.Ltmp5:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:29:21 ]
	sl_srl_b32 {s2, wcr}, s2, 0x1a
.Ltmp6:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:29:42 ]
	sl_srl_b32 {s3, wcr}, s3, 0x19
.Ltmp7:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:29:21 ]
	sl_add_i32 s0, s0, s2
.Ltmp8:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:29:42 ]
	sl_add_i32 s1, s1, s3
.Ltmp9:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:29:21 ]
	sl_sra_b32 {s7, wcr}, s0, 0x6
.Ltmp10:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:29:42 ]
	sl_sra_b32 {s0, wcr}, s1, 0x7
.Ltmp11:
	.loc	1 30 33 is_stmt 1               ; candidate.py:30:33
	sl_sra_b32 {s11, wcr}, s1, 0x1f
	sl_shl_b32 {s23, wcr}, s0, 0x3
	sl_sub_bi_u32 s0, s8, s8, wcr
	sl_abs_i32 s1, s23
	ml_cvt_f32_u32  v0, s1
	sl_reg_read s2, hwreg(HW_REG_MODE)
	ml_rcp_f32 v0, v0
	sl_or_b32 {s3, wcr}, s2, 0x3
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
	sl_sub_bi_u64 s[4:5], s[8:9], s[8:9], wcr
	sl_cmp_ge_u32 wcr, s6, s2
	sl_sub_bi_u32 s1, s8, s8, wcr
	sl_sub_bi_u64 s[24:25], s[8:9], s[8:9], wcr
	sl_and_b64 {s[4:5], wcr}, s[4:5], s[24:25]
	sl_or_b32 {s4, wcr}, s4, s5
	sl_csel_b32 s2, s26, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_add_i32 s2, s3, 0x1
	sl_add_i32 s4, s3, 0xffffffff
	sl_csel_b32 s2, s3, s2, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s2, s4, wcr
	sl_xor_b32 {s1, wcr}, s1, s11
	sl_sub_i32 s1, s1, s11
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s11, s1, 0xffffffff, wcr
	.loc	1 31 35                         ; candidate.py:31:35
	sl_mull_u32 s24, s11, 0x8
	.loc	1 31 26 is_stmt 0               ; candidate.py:31:26
	sl_sub_i32 s0, s7, s24
	.loc	1 31 37                         ; candidate.py:31:37
	sl_min_i32 s7, s0, 0x8
	.loc	1 32 22 is_stmt 1               ; candidate.py:32:22
	sl_abs_i32 s25, s7
	ml_cvt_f32_u32  v0, s25
	sl_reg_read s1, hwreg(HW_REG_MODE)
	ml_rcp_f32 v0, v0
	sl_cmp_eq_u32 wcr, s7, 0x0
	sl_sub_bi_u32 s0, s8, s8, wcr
	sl_or_b32 {s2, wcr}, s1, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s2
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_mov_v2s_b32 s1, v0, 0x0
	sl_mul_u64_u32 s[2:3], s1, s25
	sl_neg_i32 s4, s2
	sl_cmp_eq_u32 wcr, s3, 0x0
	sl_csel_b32 s2, s4, s2, wcr
	sl_mul_u64_u32 s[2:3], s2, s1
	sl_add_i32 s2, s1, s3
	sl_sub_i32 s1, s1, s3
	sl_csel_b32 s27, s2, s1, wcr
	sl_mul_u64_u32 s[2:3], s27, s6
	sl_mull_u32 s1, s3, s25
	sl_sub_i32 s28, s6, s1
	sl_cmp_ge_u32 wcr, s28, s25
	sl_sub_bi_u64 s[2:3], s[8:9], s[8:9], wcr
	sl_cmp_ge_u32 wcr, s6, s1
	sl_sub_bi_u32 s1, s8, s8, wcr
	sl_sub_bi_u64 s[4:5], s[8:9], s[8:9], wcr
	sl_and_b64 {s[2:3], wcr}, s[2:3], s[4:5]
	sl_or_b32 {s2, wcr}, s2, s3
	sl_csel_b32 s2, s26, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_sub_i32 s2, s28, s25
	sl_add_i32 s3, s28, s25
	sl_csel_b32 s2, s28, s2, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s2, s3, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s1, s26, s1, wcr
	.loc	1 32 18 is_stmt 0               ; candidate.py:32:18
	sl_add_i32 s24, s24, s1
	.loc	1 33 12 is_stmt 1               ; candidate.py:33:12
	sl_mull_u32 s1, s11, s23
	sl_sub_i32 s1, s6, s1
	.loc	1 33 20 is_stmt 0               ; candidate.py:33:20
	sl_xor_b32 {s2, wcr}, s1, s7
	sl_sra_b32 {s11, wcr}, s2, 0x1f
	sl_abs_i32 s1, s1
	sl_mul_u64_u32 s[2:3], s27, s1
	sl_mull_u32 s2, s3, s25
	sl_sub_i32 s4, s1, s2
	sl_cmp_ge_u32 wcr, s4, s25
	sl_sub_bi_u64 s[4:5], s[8:9], s[8:9], wcr
	sl_cmp_ge_u32 wcr, s1, s2
	sl_sub_bi_u32 s1, s8, s8, wcr
	sl_sub_bi_u64 s[6:7], s[8:9], s[8:9], wcr
	sl_and_b64 {s[4:5], wcr}, s[4:5], s[6:7]
	sl_or_b32 {s4, wcr}, s4, s5
	sl_csel_b32 s2, s26, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_add_i32 s2, s3, 0x1
	sl_add_i32 s4, s3, 0xffffffff
	sl_csel_b32 s2, s3, s2, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s2, s4, wcr
	sl_xor_b32 {s1, wcr}, s1, s11
	sl_sub_i32 s1, s1, s11
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s23, s26, s1, wcr
	.loc	1 36 44 is_stmt 1               ; candidate.py:36:44
	sl_abs_i32 s6, s18
	ml_cvt_f32_u32  v0, s6
	.loc	1 34 10                         ; candidate.py:34:10
	sl_mull_u32 s11, s24, 0x40
	.loc	1 36 44                         ; candidate.py:36:44
	ml_rcp_f32 v0, v0
	.loc	1 34 25                         ; candidate.py:34:25
	sl_and_b32 {s28, wcr}, tcr_lo, 0x100
	.loc	1 36 44                         ; candidate.py:36:44
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_sra_b32 {s7, wcr}, s11, 0x1f
	sl_abs_i32 s4, s11
	sl_or_b32 {s1, wcr}, s0, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s0
	ml_mov_v2s_b32 s2, v0, 0x0
	.loc	1 43 18                         ; candidate.py:43:18
	sl_mull_u32 s27, s21, 0x2
	ml_mov_b32 v17, 0x0
	ml_mov_b32 v18, 0x0
	.loc	1 36 44                         ; candidate.py:36:44
	sl_mul_u64_u32 s[0:1], s2, s6
	sl_neg_i32 s3, s0
	sl_cmp_eq_u32 wcr, s1, 0x0
	sl_csel_b32 s0, s3, s0, wcr
	sl_mul_u64_u32 s[0:1], s0, s2
	sl_add_i32 s0, s2, s1
	sl_sub_i32 s1, s2, s1
	sl_csel_b32 s0, s0, s1, wcr
	sl_mul_u64_u32 s[0:1], s0, s4
	sl_mull_u32 s0, s1, s6
	sl_sub_i32 s1, s4, s0
	sl_cmp_ge_u32 wcr, s1, s6
	sl_sub_bi_u64 s[2:3], s[8:9], s[8:9], wcr
	sl_cmp_ge_u32 wcr, s4, s0
	sl_sub_bi_u32 s0, s8, s8, wcr
	sl_sub_bi_u64 s[4:5], s[8:9], s[8:9], wcr
	sl_and_b64 {s[2:3], wcr}, s[2:3], s[4:5]
	sl_or_b32 {s2, wcr}, s2, s3
	sl_csel_b32 s2, s26, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_sub_i32 s2, s1, s6
	sl_add_i32 s3, s1, s6
	sl_csel_b32 s1, s1, s2, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s1, s3, wcr
	sl_xor_b32 {s0, wcr}, s0, s7
	sl_sub_i32 s0, s0, s7
	sl_cmp_ne_u32 wcr, s18, 0x0
	sl_csel_b32 s0, s0, 0xffffffff, wcr
	.loc	1 38 21                         ; candidate.py:38:21
	sl_mull_u32 s0, s0, s21
	.loc	1 38 9 is_stmt 0                ; candidate.py:38:9
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[24:25], s[12:13], s[0:1]
	.loc	1 43 18 is_stmt 1               ; candidate.py:43:18
	sl_bfe2_b32 s0, tcr_lo, 0x46
	sl_bfe2_b32 s2, tcr_lo, 0x28
	sl_mull_u32 s6, s2, 0x20
	sl_mull_u32 s1, s0, s21
	sl_mull_u32 s1, s1, 0x10
	sl_add_i32 s1, s1, s6
	sl_mull_u32 s7, s0, 0x800
	sl_mull_u32 s0, s2, 0x400
	sl_add_i32 s12, s7, s0
	sl_add_i32 s5, s12, 0x8000
	sl_mull_u32 s4, s1, 0x2
	sl_sme_load_16x1b64_rowxfb16 s[24:27], s[4:5], 0x0, 0x0, 0x0, 0x1
	.loc	1 40 13                         ; candidate.py:40:13
	sl_mull_u32 s0, s20, s23
	sl_mull_u32 s0, s0, 0x80
	.loc	1 40 9 is_stmt 0                ; candidate.py:40:9
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[0:1], s[14:15], s[0:1]
	.loc	1 43 18 is_stmt 1               ; candidate.py:43:18
	sl_mull_u32 s5, s2, 0x200
	sl_mov_b32 s3, 0x100
	.loc	1 43 32 is_stmt 0               ; candidate.py:43:32
	sl_mov_b32 s2, s26
	sl_add_i32 s5, s7, s5
	sl_add_i32 s6, s7, s6
	sl_mull_u32 s13, s5, 0x2
	sl_mull_u32 s6, s6, 0x2
	sl_mov_b32 s7, s13
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[6:7], 0x0, 0x0, 0x0, 0x1
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[6:7], 0x0, 0x2, 0x200, 0x1
.Ltmp12:
	.loc	2 65 17 is_stmt 1               ; standard.py:65:17 @[ candidate.py:42:35 ]
	sl_add_i32 s2, s20, 0x3f
.Ltmp13:
	.loc	1 42 25                         ; candidate.py:42:25
	sl_cmp_gt_i32 wcr, s2, 0x3f
	sl_mov_b32 s14, 0x0
	ml_mov_b32 v19, 0x0
	ml_mov_b32 v20, 0x0
	ml_mov_b32 v8, 0x0
	ml_mov_b32 v9, 0x0
	ml_mov_b32 v10, 0x0
	ml_mov_b32 v11, 0x0
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v2, 0x0
	ml_mov_b32 v4, 0x0
	ml_mov_b32 v3, 0x0
	ml_mov_b32 v5, 0x0
	ml_mov_b32 v6, 0x0
	ml_mov_b32 v7, 0x0
	sl_cbr_wcrz BB0_4, wcr
; %bb.1:                                ; %.lr.ph
.Ltmp14:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:42:35 ]
	sl_sra_b32 {s5, wcr}, s2, 0x1f
	sl_srl_b32 {s5, wcr}, s5, 0x1a
	sl_add_i32 s2, s2, s5
	sl_sra_b32 {s15, wcr}, s2, 0x6
	ml_shl_b32 v0, v16, 0x2
	ml_and_b32 v0, v0, 0xfc
	sl_mull_u32 s2, s28, 0x8
	ml_add_i32 v17, s2, v0
	sl_and_b32 {s2, wcr}, s10, 0x40
	sl_mov_b32 s2, 0x280
	sl_csel_b32 s2, s2, 0x0, wcr
	sl_mull_u32 s5, s10, 0x8
	sl_and_b32 {s20, wcr}, s5, 0x400
	ml_xor_b32 v18, s2, v0
.Ltmp15:
	.loc	1 42 25                         ; candidate.py:42:25
	sl_add_i64 s[0:1], s[0:1], 0x4000
	sl_add_i64 s[24:25], s[24:25], 0x80
	ml_mov_b32 v0, 0x0
	ml_xor_b32 v19, v17, 0x80
	sl_mov_b32 s21, s26
	ml_mov_b32 v12, 0x0
	ml_mov_b32 v13, 0x0
	ml_mov_b32 v14, 0x0
	ml_mov_b32 v15, 0x0
BB0_2:                                  ; =>This Inner Loop Header: Depth=1
	sl_add_i32 s2, s21, 0x1
	sl_cmp_lt_i32 wcr, s2, 0x2
	sl_csel_b32 s21, s2, 0x0, wcr
	.loc	1 43 18                         ; candidate.py:43:18
	sl_wait g2scnt(0)
	sl_barrier_req 0x0
	sl_barrier_wait 0x0
	sl_mull_u32 s30, s21, 0x2000
	sl_add_i32 s29, s30, 0x8000
	ml_slb_load_b32x1  v20, v17, s29, #0, null
	.loc	1 43 32 is_stmt 0               ; candidate.py:43:32
	sl_mull_u32 s2, s21, 0x4000
	sl_add_i32 s31, s20, s2
	sl_add_i32 s32, s31, 0x800
	.loc	1 43 18                         ; candidate.py:43:18
	ml_slb_load_b32x1  v21, v17, s29, #256, null
	sl_add_i32 s33, s30, 0x9000
	.loc	1 42 25 is_stmt 1               ; candidate.py:42:25
	sl_add_i32 s2, s14, 0x1
	sl_cmp_lt_i32 wcr, s2, 0x2
	.loc	1 43 32                         ; candidate.py:43:32
	ml_slb_load_b32x1  v22, v18, s31, #0, null
	.loc	1 42 25                         ; candidate.py:42:25
	sl_csel_b32 s14, s2, 0x0, wcr
	.loc	1 43 18                         ; candidate.py:43:18
	sl_mull_u32 s2, s14, 0x2000
	sl_add_i32 s2, s12, s2
	.loc	1 43 32 is_stmt 0               ; candidate.py:43:32
	ml_slb_load_b32x1  v23, v18, s31, #256, null
	.loc	1 43 18                         ; candidate.py:43:18
	sl_add_i32 s5, s2, 0x8000
	sl_sme_load_16x1b64_rowxfb16 s[24:27], s[4:5], 0x0, 0x0, 0x0, 0x1
	.loc	1 43 32                         ; candidate.py:43:32
	sl_mull_u32 s5, s14, 0x4000
	ml_slb_load_b32x1  v24, v18, s32, #0, null
	sl_mov_b32 s2, s26
	sl_add_i32 s7, s5, s13
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[6:7], 0x0, 0x0, 0x0, 0x1
	ml_slb_load_b32x1  v25, v18, s32, #256, null
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[6:7], 0x0, 0x2, 0x200, 0x1
	sl_add_i32 s2, s31, 0x1000
	sl_add_i32 s5, s31, 0x1800
	.loc	1 43 18                         ; candidate.py:43:18
	ml_slb_load_b32x1  v26, v17, s33, #0, null
	sl_add_i32 s7, s30, 0x8400
	.loc	1 43 32                         ; candidate.py:43:32
	sl_add_i32 s34, s31, 0x2000
	sl_add_i32 s35, s31, 0x2800
	.loc	1 43 18                         ; candidate.py:43:18
	ml_slb_load_b32x1  v27, v17, s33, #256, null
	sl_add_i32 s30, s30, 0x9400
	.loc	1 43 32                         ; candidate.py:43:32
	sl_add_i32 s36, s31, 0x3000
	sl_add_i32 s37, s31, 0x3800
	.loc	1 44 22 is_stmt 1               ; candidate.py:44:22
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[20:21], v[22:23], v[0:3]
	.loc	1 42 25                         ; candidate.py:42:25
	sl_add_i64 s[0:1], s[0:1], 0x4000
	sl_add_i32 s15, s15, 0xffffffff
	sl_cmp_eq_u32 wcr, s15, 0x0
	sl_add_i64 s[24:25], s[24:25], 0x80
	.loc	1 44 22                         ; candidate.py:44:22
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[20:21], v[24:25], v[4:7]
	.loc	1 43 18                         ; candidate.py:43:18
	ml_slb_load_b32x1  v20, v19, s29, #512, null
	ml_slb_load_b32x1  v21, v19, s29, #768, null
	.loc	1 44 22                         ; candidate.py:44:22
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[26:27], v[22:23], v[8:11]
	.loc	1 43 32                         ; candidate.py:43:32
	ml_slb_load_b32x1  v22, v18, s2, #0, null
	ml_slb_load_b32x1  v23, v18, s2, #256, null
	.loc	1 44 22                         ; candidate.py:44:22
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[26:27], v[24:25], v[12:15]
	.loc	1 43 32                         ; candidate.py:43:32
	ml_slb_load_b32x1  v24, v18, s5, #0, null
	ml_slb_load_b32x1  v25, v18, s5, #256, null
	.loc	1 43 18 is_stmt 0               ; candidate.py:43:18
	ml_slb_load_b32x1  v26, v19, s33, #512, null
	ml_slb_load_b32x1  v27, v19, s33, #768, null
	.loc	1 44 22 is_stmt 1               ; candidate.py:44:22
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[20:21], v[22:23], v[0:3]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[20:21], v[24:25], v[4:7]
	.loc	1 43 18                         ; candidate.py:43:18
	ml_slb_load_b32x1  v20, v17, s7, #0, null
	ml_slb_load_b32x1  v21, v17, s7, #256, null
	.loc	1 44 22                         ; candidate.py:44:22
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[26:27], v[22:23], v[8:11]
	.loc	1 43 32                         ; candidate.py:43:32
	ml_slb_load_b32x1  v22, v18, s34, #0, null
	ml_slb_load_b32x1  v23, v18, s34, #256, null
	.loc	1 44 22                         ; candidate.py:44:22
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[26:27], v[24:25], v[12:15]
	.loc	1 43 32                         ; candidate.py:43:32
	ml_slb_load_b32x1  v24, v18, s35, #0, null
	ml_slb_load_b32x1  v25, v18, s35, #256, null
	.loc	1 43 18 is_stmt 0               ; candidate.py:43:18
	ml_slb_load_b32x1  v26, v17, s30, #0, null
	ml_slb_load_b32x1  v27, v17, s30, #256, null
	.loc	1 44 22 is_stmt 1               ; candidate.py:44:22
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[20:21], v[22:23], v[0:3]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[20:21], v[24:25], v[4:7]
	.loc	1 43 18                         ; candidate.py:43:18
	ml_slb_load_b32x1  v20, v19, s7, #512, null
	ml_slb_load_b32x1  v21, v19, s7, #768, null
	.loc	1 44 22                         ; candidate.py:44:22
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[26:27], v[22:23], v[8:11]
	.loc	1 43 32                         ; candidate.py:43:32
	ml_slb_load_b32x1  v22, v18, s36, #0, null
	ml_slb_load_b32x1  v23, v18, s36, #256, null
	.loc	1 44 22                         ; candidate.py:44:22
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[26:27], v[24:25], v[12:15]
	.loc	1 43 32                         ; candidate.py:43:32
	ml_slb_load_b32x1  v24, v18, s37, #0, null
	ml_slb_load_b32x1  v25, v18, s37, #256, null
	.loc	1 43 18 is_stmt 0               ; candidate.py:43:18
	ml_slb_load_b32x1  v26, v19, s30, #512, null
	ml_slb_load_b32x1  v27, v19, s30, #768, null
	.loc	1 44 22 is_stmt 1               ; candidate.py:44:22
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[20:21], v[22:23], v[0:3]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[20:21], v[24:25], v[4:7]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[26:27], v[22:23], v[8:11]
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[26:27], v[24:25], v[12:15]
	.loc	1 42 25                         ; candidate.py:42:25
	sl_cbr_wcrz BB0_2, wcr
; %bb.3:                                ; %._crit_edge.loopexit
	.loc	1 48 48                         ; candidate.py:48:48
	ml_cvt_bf16_f32  v17, v0
	ml_cvt_bf16_f32  v18, v1
	ml_cvt_bf16_f32  v19, v2
	ml_cvt_bf16_f32  v20, v3
	ml_cvt_bf16_f32  v8, v8
	ml_cvt_bf16_f32  v9, v9
	ml_cvt_bf16_f32  v10, v10
	ml_cvt_bf16_f32  v11, v11
	ml_cvt_bf16_f32  v0, v4
	ml_cvt_bf16_f32  v1, v5
	ml_cvt_bf16_f32  v2, v6
	ml_cvt_bf16_f32  v4, v7
	ml_cvt_bf16_f32  v3, v12
	ml_cvt_bf16_f32  v5, v13
	ml_cvt_bf16_f32  v6, v14
	ml_cvt_bf16_f32  v7, v15
BB0_4:                                  ; %._crit_edge
	.loc	1 35 10                         ; candidate.py:35:10
	sl_mull_u32 s0, s23, 0x80
	.loc	1 35 25 is_stmt 0               ; candidate.py:35:25
	ml_shl_b32 v21, v16, 0x1
	ml_and_b32 v12, v21, 0xe
	sl_srl_b32 {s1, wcr}, s10, 0x2
	sl_and_b32 {s1, wcr}, s1, 0x30
	sl_add_i32 s0, s0, s1
	ml_add_i32 v22, s0, v12
	.loc	1 35 13                         ; candidate.py:35:13
	ml_add_i32 v23, v22, 0x40
	.loc	1 34 25 is_stmt 1               ; candidate.py:34:25
	sl_srl_b32 {s0, wcr}, s28, 0x4
	ml_bfe2_b32 v12, v16, 0x63
	.loc	1 34 13 is_stmt 0               ; candidate.py:34:13
	sl_add_i32 s0, s11, s0
	ml_add_i32 v24, s0, v12
	ml_add_i32 v25, v24, 0x28
	ml_add_i32 v26, v24, 0x20
	ml_add_i32 v27, v24, 0x8
	.loc	1 42 25 is_stmt 1               ; candidate.py:42:25
	sl_wait g2scnt(0)
	sl_barrier 
	.loc	1 48 26                         ; candidate.py:48:26
	ml_mul_u64_u32 v[12:13], s22, v24
	.loc	1 48 48 is_stmt 0               ; candidate.py:48:48
	sl_mov_b32 s23, 0x2010200
	.loc	1 48 26                         ; candidate.py:48:26
	ml_mul_u64_u32 v[13:14], s22, v27
	ml_mul_u64_u32 v[14:15], s22, v26
	ml_mul_u64_u32 v[15:16], s22, v25
	.loc	1 48 48                         ; candidate.py:48:48
	sl_mov_b32 s22, 0x1000504
	.loc	1 47 21 is_stmt 1               ; candidate.py:47:21
	ml_cmp_gt_i32 tcr, s18, v24
	.loc	1 48 15                         ; candidate.py:48:15
	ml_sra_b32 v16, v12, 0x1f
	ml_shl_b32 v24, v12, 0x1
	ml_shl_b32 v16, v16, 0x1
	.loc	1 47 21                         ; candidate.py:47:21
	sl_mov_b64 s[10:11], tcr
	ml_cmp_gt_i32 tcr, s18, v27
	.loc	1 48 48                         ; candidate.py:48:48
	ml_byte_permute_b32 v17, v18, v17, s22
	ml_byte_permute_b32 v18, v20, v19, s22
	ml_and_b32 v19, tid, 0x1
	.loc	1 47 21                         ; candidate.py:47:21
	sl_mov_b64 s[6:7], tcr
	ml_cmp_gt_i32 tcr, s18, v26
	.loc	1 48 30                         ; candidate.py:48:30
	ml_shl_b32 v26, v22, 0x1
	ml_mov_b32 v20, 0x5410
	.loc	1 48 48 is_stmt 0               ; candidate.py:48:48
	ml_bfe2_b32 v27, tid, 0x25
	.loc	1 47 21 is_stmt 1               ; candidate.py:47:21
	sl_mov_b64 s[2:3], tcr
	ml_cmp_gt_i32 tcr, s18, v25
	.loc	1 48 15                         ; candidate.py:48:15
	ml_srl_b32 v25, v12, 0x1f
	ml_or_b32 v16, v16, v25
	ml_mov_b32 v25, s17
	.loc	1 47 21                         ; candidate.py:47:21
	sl_mov_b64 s[0:1], tcr
	.loc	1 47 36 is_stmt 0               ; candidate.py:47:36
	ml_cmp_gt_i32 tcr, s19, v22
	.loc	1 48 48 is_stmt 1               ; candidate.py:48:48
	ml_anyop3_b32 v21, 62, v21, v27, 0xfffffff8
	ml_byte_permute_b32 v8, v9, v8, s22
	ml_byte_permute_b32 v9, v11, v10, s22
	.loc	1 47 36                         ; candidate.py:47:36
	sl_mov_b64 s[12:13], tcr
	ml_cmp_gt_i32 tcr, s19, v23
	ml_mov_b32 v11, 0x3276
	.loc	1 47 25 is_stmt 0               ; candidate.py:47:25
	sl_and_b64 {s[14:15], wcr}, s[10:11], s[12:13]
	.loc	1 48 61 is_stmt 1               ; candidate.py:48:61
	sl_mov_b32 s19, s26
	.loc	1 47 36                         ; candidate.py:47:36
	sl_mov_b64 s[4:5], tcr
	.loc	1 48 15                         ; candidate.py:48:15
	ml_addo_u32 {v24, tcr}, s16, v24
	ml_addc_i32 v16, v25, v16, tcr
	.loc	1 48 30 is_stmt 0               ; candidate.py:48:30
	ml_sra_b32 v25, v22, 0x1f
	ml_addo_u32 {v24, tcr}, v26, v24
	ml_shl_b32 v25, v25, 0x1
	ml_srl_b32 v26, v22, 0x1f
	ml_or_b32 v25, v25, v26
	ml_addc_i32 v16, v16, v25, tcr
	.loc	1 48 48                         ; candidate.py:48:48
	ml_cmp_eq_u32 tcr, v19, 0x0
	ml_mov_b32 v19, 0x7632
	ml_csel_b32 v25, v20, v19, tcr
	ml_byte_permute_b32 v25, v25, v25, s23
	ml_pk_shl_b16 v25, v25, 0x40004
	ml_pk_srl_b8 v25, v25, 0x40004
	ml_byte_permute_b32 v26, v17, v18, v25
	ml_slb_shuffle_rtn_b32 v26, v26, v21
	ml_csel_b32 v27, v19, v20, tcr
	ml_byte_permute_b32 v27, v27, v27, s23
	ml_pk_shl_b16 v27, v27, 0x40004
	ml_pk_srl_b8 v27, v27, 0x40004
	ml_byte_permute_b32 v17, v17, v18, v27
	ml_xor_b32 v18, v21, 0x1
	ml_slb_shuffle_rtn_b32 v17, v17, v18
	ml_byte_permute_b32 v10, v8, v9, v25
	ml_byte_permute_b32 v8, v8, v9, v27
	ml_and_b32 v9, tid, 0x20
	ml_slb_shuffle_rtn_b32 v10, v10, v21
	ml_cmp_eq_u32 tcr, v9, 0x0
	ml_mov_b32 v9, 0x1054
	ml_csel_b32 v9, v20, v9, tcr
	ml_csel_b32 v11, v19, v11, tcr
	ml_slb_shuffle_rtn_b32 v8, v8, v18
	ml_byte_permute_b32 v9, v9, v9, s23
	.loc	1 48 61                         ; candidate.py:48:61
	ml_mov_v2s_b32 s16, v24, 0x0
	.loc	1 48 48                         ; candidate.py:48:48
	ml_pk_shl_b16 v9, v9, 0x40004
	ml_pk_srl_b8 v9, v9, 0x40004
	.loc	1 48 61                         ; candidate.py:48:61
	ml_mov_v2s_b32 s17, v16, 0x0
	ml_mov_b32 v16, s16
	ml_sub_i32 v16, v24, v16
	.loc	1 48 48                         ; candidate.py:48:48
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v19, v26, v17, v9
	.loc	1 48 61                         ; candidate.py:48:61
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[14:15], tmsk
	ml_lsa_store_dword v19, s[16:19], signed v16, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	ml_sub_i32 v19, v13, v12
	ml_shl_b32 v19, v19, 0x1
	ml_mov_v2s_b32 s18, v19, 0x0
	.loc	1 47 25 is_stmt 1               ; candidate.py:47:25
	sl_and_b64 {s[14:15], wcr}, s[12:13], s[6:7]
	sl_and_b64 {s[20:21], wcr}, s[12:13], s[2:3]
	.loc	1 48 48                         ; candidate.py:48:48
	ml_byte_permute_b32 v11, v11, v11, s23
	ml_pk_shl_b16 v11, v11, 0x40004
	ml_pk_srl_b8 v11, v11, 0x40004
	ml_byte_permute_b32 v17, v26, v17, v11
	.loc	1 48 61 is_stmt 0               ; candidate.py:48:61
	ml_add_i32 v19, s18, v16
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[14:15], tmsk
	ml_lsa_store_dword v17, s[16:19], signed v19, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 48 48                         ; candidate.py:48:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v17, v10, v8, v9
	.loc	1 48 61                         ; candidate.py:48:61
	ml_sub_i32 v19, v14, v12
	ml_shl_b32 v19, v19, 0x1
	ml_mov_v2s_b32 s14, v19, 0x0
	ml_sub_i32 v19, v15, v12
	ml_shl_b32 v19, v19, 0x1
	ml_mov_v2s_b32 s15, v19, 0x0
	ml_add_i32 v19, s14, v16
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[20:21], tmsk
	ml_lsa_store_dword v17, s[16:19], signed v19, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 25 is_stmt 1               ; candidate.py:47:25
	sl_and_b64 {s[12:13], wcr}, s[12:13], s[0:1]
	.loc	1 48 48                         ; candidate.py:48:48
	ml_byte_permute_b32 v8, v10, v8, v11
	.loc	1 48 61 is_stmt 0               ; candidate.py:48:61
	ml_add_i32 v10, s15, v16
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[12:13], tmsk
	ml_lsa_store_dword v8, s[16:19], signed v10, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 48 48                         ; candidate.py:48:48
	ml_byte_permute_b32 v0, v1, v0, s22
	ml_byte_permute_b32 v1, v4, v2, s22
	ml_byte_permute_b32 v2, v0, v1, v25
	ml_slb_shuffle_rtn_b32 v2, v2, v21
	ml_byte_permute_b32 v3, v5, v3, s22
	ml_byte_permute_b32 v4, v7, v6, s22
	ml_byte_permute_b32 v0, v0, v1, v27
	ml_slb_shuffle_rtn_b32 v0, v0, v18
	ml_byte_permute_b32 v1, v3, v4, v25
	ml_byte_permute_b32 v3, v3, v4, v27
	.loc	1 48 30                         ; candidate.py:48:30
	ml_add_i32 v4, v22, v12
	.loc	1 48 48                         ; candidate.py:48:48
	ml_slb_shuffle_rtn_b32 v1, v1, v21
	.loc	1 48 30                         ; candidate.py:48:30
	ml_add_i32 v5, v23, v13
	ml_add_i32 v6, v23, v14
	ml_add_i32 v7, v23, v15
	.loc	1 48 48                         ; candidate.py:48:48
	ml_slb_shuffle_rtn_b32 v3, v3, v18
	.loc	1 48 61                         ; candidate.py:48:61
	ml_sub_i32 v8, v23, v22
	.loc	1 47 25 is_stmt 1               ; candidate.py:47:25
	sl_and_b64 {s[10:11], wcr}, s[10:11], s[4:5]
	.loc	1 48 61                         ; candidate.py:48:61
	ml_shl_b32 v8, v8, 0x1
	ml_mov_v2s_b32 s12, v8, 0x0
	ml_sub_i32 v5, v5, v4
	ml_shl_b32 v5, v5, 0x1
	ml_mov_v2s_b32 s13, v5, 0x0
	ml_add_i32 v5, s12, v16
	.loc	1 48 48 is_stmt 0               ; candidate.py:48:48
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v8, v2, v0, v9
	.loc	1 48 61                         ; candidate.py:48:61
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[10:11], tmsk
	ml_lsa_store_dword v8, s[16:19], signed v5, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 25 is_stmt 1               ; candidate.py:47:25
	sl_and_b64 {s[6:7], wcr}, s[4:5], s[6:7]
	.loc	1 48 48                         ; candidate.py:48:48
	ml_byte_permute_b32 v0, v2, v0, v11
	.loc	1 48 61 is_stmt 0               ; candidate.py:48:61
	ml_add_i32 v2, s13, v16
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v0, s[16:19], signed v2, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	ml_sub_i32 v0, v6, v4
	ml_shl_b32 v0, v0, 0x1
	ml_mov_v2s_b32 s6, v0, 0x0
	ml_sub_i32 v0, v7, v4
	.loc	1 47 25 is_stmt 1               ; candidate.py:47:25
	sl_and_b64 {s[2:3], wcr}, s[4:5], s[2:3]
	.loc	1 48 48                         ; candidate.py:48:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v2, v1, v3, v9
	.loc	1 48 61 is_stmt 0               ; candidate.py:48:61
	ml_shl_b32 v0, v0, 0x1
	ml_mov_v2s_b32 s7, v0, 0x0
	ml_add_i32 v0, s6, v16
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[2:3], tmsk
	ml_lsa_store_dword v2, s[16:19], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 48 48                         ; candidate.py:48:48
	ml_byte_permute_b32 v0, v1, v3, v11
	.loc	1 47 25 is_stmt 1               ; candidate.py:47:25
	sl_and_b64 {s[0:1], wcr}, s[4:5], s[0:1]
	.loc	1 48 61                         ; candidate.py:48:61
	ml_add_i32 v1, s7, v16
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v0, s[16:19], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 48 4 is_stmt 0                ; candidate.py:48:4
	sl_eop 
.Ltmp16:
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	nonly_linear.kd
	.type	nonly_linear.kd,@object
	.size	nonly_linear.kd, 64
nonly_linear.kd:
	.asciz	"\000\000\000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	nonly_linear@rel64-nonly_linear.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	536902
	.asciz	"\003\000\224\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	nonly_linear, .Lfunc_end0-nonly_linear
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 4320
; NumSgprs: 42
; NumVgprs: 28
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 5
; VGPRBlocks: 6
; NumSGPRsForWarpsPerNU: 38
; NumVGPRsForWarpsPerNR: 28
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
	.long	226                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0xdb DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"candidate.py"                  ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/workspace/experiments/minicpm-s2/framework/20261026T102808704037Z-biv150-nonly-down-component/source" ; DW_AT_comp_dir
	.byte	0
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.byte	2                               ; Abbrev [2] 0x9c:0xf DW_TAG_subprogram
	.ascii	"nonly_linear"                  ; DW_AT_name
	.byte	0
	.byte	1                               ; DW_AT_inline
	.byte	3                               ; Abbrev [3] 0xab:0x3a DW_TAG_subprogram
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.long	156                             ; DW_AT_abstract_origin
	.byte	4                               ; Abbrev [4] 0xc0:0xc DW_TAG_inlined_subroutine
	.long	156                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges0                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	29                              ; DW_AT_call_line
	.byte	42                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0xcc:0xc DW_TAG_inlined_subroutine
	.long	156                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges1                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	29                              ; DW_AT_call_line
	.byte	21                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0xd8:0xc DW_TAG_inlined_subroutine
	.long	156                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges2                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	42                              ; DW_AT_call_line
	.byte	35                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	0                               ; End Of Children Mark
	.section	.debug_ranges,"",@progbits
.Ldebug_ranges0:
	.quad	.Ltmp0-.Lfunc_begin0
	.quad	.Ltmp1-.Lfunc_begin0
	.quad	.Ltmp2-.Lfunc_begin0
	.quad	.Ltmp3-.Lfunc_begin0
	.quad	.Ltmp4-.Lfunc_begin0
	.quad	.Ltmp5-.Lfunc_begin0
	.quad	.Ltmp6-.Lfunc_begin0
	.quad	.Ltmp7-.Lfunc_begin0
	.quad	.Ltmp8-.Lfunc_begin0
	.quad	.Ltmp9-.Lfunc_begin0
	.quad	.Ltmp10-.Lfunc_begin0
	.quad	.Ltmp11-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges1:
	.quad	.Ltmp1-.Lfunc_begin0
	.quad	.Ltmp2-.Lfunc_begin0
	.quad	.Ltmp3-.Lfunc_begin0
	.quad	.Ltmp4-.Lfunc_begin0
	.quad	.Ltmp5-.Lfunc_begin0
	.quad	.Ltmp6-.Lfunc_begin0
	.quad	.Ltmp7-.Lfunc_begin0
	.quad	.Ltmp8-.Lfunc_begin0
	.quad	.Ltmp9-.Lfunc_begin0
	.quad	.Ltmp10-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges2:
	.quad	.Ltmp12-.Lfunc_begin0
	.quad	.Ltmp13-.Lfunc_begin0
	.quad	.Ltmp14-.Lfunc_begin0
	.quad	.Ltmp15-.Lfunc_begin0
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
      - .address_space:  global
        .name:           KArg_8
        .offset:         48
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_9
        .offset:         56
        .size:           8
        .value_kind:     global_buffer
    .group_segment_fixed_size: 0
    .kernarg_segment_align: 8
    .kernarg_segment_size: 64
    .max_flat_workgroup_size: 0
    .name:           nonly_linear
    .private_segment_fixed_size: 0
    .sgpr_count:     42
    .sgpr_spill_count: 0
    .symbol:         nonly_linear.kd
    .vgpr_count:     28
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
