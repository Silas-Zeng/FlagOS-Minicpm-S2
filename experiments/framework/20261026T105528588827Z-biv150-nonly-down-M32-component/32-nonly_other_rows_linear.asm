	.text
	.globl	nonly_other_rows_linear         ; -- Begin function nonly_other_rows_linear
	.p2align	3
	.type	nonly_other_rows_linear,@function
	.iluvatar_kernel nonly_other_rows_linear
nonly_other_rows_linear:                ; @nonly_other_rows_linear
.Lfunc_begin0:
	.file	1 "/workspace/experiments/minicpm-s2/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/source" "candidate.py"
	.loc	1 25 0                          ; candidate.py:25:0
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
		granulated_workitem_vgpr_count = 4
		granulated_warp_sgpr_count = 4
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
		warp_sgpr_count = 36
		workitem_vgpr_count = 18
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
	ml_vrf_init_u32 v4, tcr
.Ltmp0:
	.file	2 "/usr/local/lib/python3.12/site-packages/triton/language" "standard.py"
	.loc	2 65 17 prologue_end            ; standard.py:65:17 @[ candidate.py:27:21 ]
	sl_lsa_load_b32x16 s[12:27], s[4:5], noreg, #0, ca
	sl_wait smcnt(0)
	sl_add_i32 s0, s18, 0x1f
.Ltmp1:
	.loc	2 65 17 is_stmt 0               ; standard.py:65:17 @[ candidate.py:27:42 ]
	sl_add_i32 s1, s19, 0x3f
.Ltmp2:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:21 ]
	sl_sra_b32 {s2, wcr}, s0, 0x1f
.Ltmp3:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:42 ]
	sl_sra_b32 {s3, wcr}, s1, 0x1f
.Ltmp4:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:21 ]
	sl_srl_b32 {s2, wcr}, s2, 0x1b
.Ltmp5:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:42 ]
	sl_srl_b32 {s3, wcr}, s3, 0x1a
.Ltmp6:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:21 ]
	sl_add_i32 s0, s0, s2
.Ltmp7:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:42 ]
	sl_add_i32 s1, s1, s3
.Ltmp8:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:21 ]
	sl_sra_b32 {s7, wcr}, s0, 0x5
.Ltmp9:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:42 ]
	sl_sra_b32 {s0, wcr}, s1, 0x6
.Ltmp10:
	.loc	1 28 33 is_stmt 1               ; candidate.py:28:33
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
	.loc	1 29 35                         ; candidate.py:29:35
	sl_mull_u32 s24, s11, 0x8
	.loc	1 29 26 is_stmt 0               ; candidate.py:29:26
	sl_sub_i32 s0, s7, s24
	.loc	1 29 37                         ; candidate.py:29:37
	sl_min_i32 s7, s0, 0x8
	.loc	1 30 22 is_stmt 1               ; candidate.py:30:22
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
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v2, 0x0
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
	.loc	1 30 18 is_stmt 0               ; candidate.py:30:18
	sl_add_i32 s24, s24, s1
	.loc	1 31 12 is_stmt 1               ; candidate.py:31:12
	sl_mull_u32 s1, s11, s23
	sl_sub_i32 s1, s6, s1
	.loc	1 31 20 is_stmt 0               ; candidate.py:31:20
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
	sl_csel_b32 s0, s26, s1, wcr
	.loc	1 32 10 is_stmt 1               ; candidate.py:32:10
	sl_mull_u32 s23, s24, 0x20
	.loc	1 32 25 is_stmt 0               ; candidate.py:32:25
	sl_and_b32 {s28, wcr}, tcr_lo, 0x100
	.loc	1 33 10 is_stmt 1               ; candidate.py:33:10
	sl_mull_u32 s11, s0, 0x40
.Ltmp11:
	.loc	2 65 17                         ; standard.py:65:17 @[ candidate.py:41:35 ]
	sl_add_i32 s0, s20, 0x3f
.Ltmp12:
	.loc	1 41 25                         ; candidate.py:41:25
	sl_cmp_gt_i32 wcr, s0, 0x3f
	ml_mov_b32 v3, 0x0
	sl_cbr_wcrz BB0_6, wcr
; %bb.1:                                ; %.lr.ph
.Ltmp13:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:41:35 ]
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_srl_b32 {s1, wcr}, s1, 0x1a
	sl_add_i32 s0, s0, s1
	sl_sra_b32 {s29, wcr}, s0, 0x6
.Ltmp14:
	.loc	1 39 19                         ; candidate.py:39:19
	sl_sra_b32 {s0, wcr}, s11, 0x1f
	sl_srl_b32 {s0, wcr}, s0, 0x19
	sl_add_i32 s0, s11, s0
	sl_srl_b32 {s1, wcr}, s0, 0x7
	.loc	1 39 25 is_stmt 0               ; candidate.py:39:25
	sl_mull_u32 s1, s20, s1
	sl_mull_u32 s24, s1, 0x80
	.loc	1 39 9                          ; candidate.py:39:9
	sl_sra_b32 {s25, wcr}, s24, 0x1f
	.loc	1 39 56                         ; candidate.py:39:56
	sl_and_b32 {s0, wcr}, s0, 0xffffff80
	.loc	1 34 44 is_stmt 1               ; candidate.py:34:44
	sl_abs_i32 s6, s18
	ml_cvt_f32_u32  v0, s6
	.loc	1 39 56                         ; candidate.py:39:56
	sl_sub_i32 s30, s11, s0
	.loc	1 34 44                         ; candidate.py:34:44
	ml_rcp_f32 v0, v0
	.loc	1 39 48                         ; candidate.py:39:48
	sl_sra_b32 {s31, wcr}, s30, 0x1f
	.loc	1 34 44                         ; candidate.py:34:44
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_sra_b32 {s7, wcr}, s23, 0x1f
	sl_abs_i32 s4, s23
	sl_or_b32 {s1, wcr}, s0, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s0
	ml_mov_v2s_b32 s2, v0, 0x0
	.loc	1 32 25                         ; candidate.py:32:25
	sl_bfe2_b32 s20, s10, 0x66
	ml_shl_b32 v0, v4, 0x2
	ml_and_b32 v0, v0, 0xfc
	.loc	1 34 44                         ; candidate.py:34:44
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
	.loc	1 36 21                         ; candidate.py:36:21
	sl_mull_u32 s0, s0, s21
	.loc	1 36 9 is_stmt 0                ; candidate.py:36:9
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	.loc	1 32 25 is_stmt 1               ; candidate.py:32:25
	sl_srl_b32 {s2, wcr}, s10, 0x6
	sl_bfe2_b32 s4, s10, 0x26
	sl_bfe2_b32 s6, s2, 0x41
	sl_mull_u32 s3, s21, 0x2
	sl_mull_u32 s5, s4, 0x800
	sl_mull_u32 s7, s6, 0x400
	sl_add_i32 s5, s5, s7
	sl_mull_u32 s6, s6, 0x40
	sl_mull_u32 s4, s4, s21
	sl_mull_u32 s4, s4, 0x20
	sl_add_i32 s4, s4, s6
	sl_bfe2_b32 s7, s10, 0x46
	sl_bfe2_b32 s2, s2, 0x22
	sl_mull_u32 s6, s2, 0x40
	sl_mull_u32 s21, s7, 0x1000
	sl_add_i32 s6, s6, s21
	sl_mull_u32 s7, s7, 0x800
	sl_mull_u32 s2, s2, 0x400
	sl_add_i32 s7, s7, s2
	sl_mull_u32 s2, s28, 0x8
	ml_add_i32 v5, s2, v0
	ml_xor_b32 v6, v5, 0x80
	sl_and_b32 {s2, wcr}, s10, 0x40
	sl_mov_b32 s2, 0x280
	sl_csel_b32 s2, s2, 0x0, wcr
	sl_mull_u32 s21, s10, 0x8
	sl_and_b32 {s21, wcr}, s21, 0x400
	ml_xor_b32 v7, s2, v0
	.loc	1 41 25                         ; candidate.py:41:25
	sl_shl_b64 {s[24:25], wcr}, s[24:25], 0x1
	sl_add_i64 s[14:15], s[14:15], s[24:25]
	sl_shl_b64 {s[24:25], wcr}, s[30:31], 0x1
	sl_add_i64 s[24:25], s[14:15], s[24:25]
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[0:1], s[12:13], s[0:1]
	ml_mov_b32 v0, 0x0
	sl_mov_b32 s27, 0x100
	sl_mov_b32 s12, 0x2000
	sl_mov_b32 s13, 0x2400
	sl_jump BB0_3
BB0_2:                                  ;   in Loop: Header=BB0_3 Depth=1
	.loc	1 42 18                         ; candidate.py:42:18
	sl_wait g2scnt(0)
	.loc	1 42 32 is_stmt 0               ; candidate.py:42:32
	sl_sme_load_16x1b64_rowxfb16 s[24:27], s[6:7], 0x0, 0x0, 0x0, 0x1
	sl_wait g2scnt(0)
	.loc	1 42 18                         ; candidate.py:42:18
	sl_barrier 
	ml_slb_load_b32x1  v8, v5, s12, #0, null
	.loc	1 42 32                         ; candidate.py:42:32
	sl_add_i32 s2, s21, 0x800
	sl_add_i32 s14, s21, 0x1000
	sl_add_i32 s15, s21, 0x1800
	.loc	1 42 18                         ; candidate.py:42:18
	ml_slb_load_b32x1  v9, v5, s12, #256, null
	.loc	1 41 25 is_stmt 1               ; candidate.py:41:25
	sl_add_i64 s[24:25], s[24:25], 0x4000
	sl_add_i32 s29, s29, 0xffffffff
	sl_cmp_eq_u32 wcr, s29, 0x0
	.loc	1 42 18                         ; candidate.py:42:18
	ml_slb_load_b32x1  v10, v5, s13, #0, null
	.loc	1 41 25                         ; candidate.py:41:25
	sl_add_i64 s[0:1], s[0:1], 0x80
	.loc	1 42 18                         ; candidate.py:42:18
	ml_slb_load_b32x1  v11, v5, s13, #256, null
	ml_slb_load_b32x1  v12, v6, s12, #512, null
	.loc	1 42 32 is_stmt 0               ; candidate.py:42:32
	ml_slb_load_b32x1  v14, v7, s21, #0, null
	ml_slb_load_b32x1  v15, v7, s21, #256, null
	.loc	1 42 18                         ; candidate.py:42:18
	ml_slb_load_b32x1  v13, v6, s12, #768, null
	.loc	1 42 32                         ; candidate.py:42:32
	ml_slb_load_b32x1  v16, v7, s2, #0, null
	ml_slb_load_b32x1  v17, v7, s2, #256, null
	.loc	1 43 22 is_stmt 1               ; candidate.py:43:22
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[8:9], v[14:15], v[0:3]
	.loc	1 42 18                         ; candidate.py:42:18
	ml_slb_load_b32x1  v8, v6, s13, #512, null
	.loc	1 42 32 is_stmt 0               ; candidate.py:42:32
	ml_slb_load_b32x1  v14, v7, s14, #0, null
	ml_slb_load_b32x1  v15, v7, s14, #256, null
	.loc	1 43 22 is_stmt 1               ; candidate.py:43:22
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[12:13], v[16:17], v[0:3]
	.loc	1 42 18                         ; candidate.py:42:18
	ml_slb_load_b32x1  v9, v6, s13, #768, null
	.loc	1 42 32 is_stmt 0               ; candidate.py:42:32
	ml_slb_load_b32x1  v12, v7, s15, #0, null
	ml_slb_load_b32x1  v13, v7, s15, #256, null
	.loc	1 43 22 is_stmt 1               ; candidate.py:43:22
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[10:11], v[14:15], v[0:3]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[8:9], v[12:13], v[0:3]
	.loc	1 41 25                         ; candidate.py:41:25
	sl_cbr_wcrnz BB0_5, wcr
BB0_3:                                  ; =>This Inner Loop Header: Depth=1
	.loc	1 42 18                         ; candidate.py:42:18
	sl_wait lmcnt(0) g2scnt(0)
	sl_barrier_req 0x0
	sl_barrier_wait 0x0
	sl_cmp_lt_u32 wcr, s20, 0x4
	sl_cbr_wcrz BB0_2, wcr
; %bb.4:                                ;   in Loop: Header=BB0_3 Depth=1
	.loc	1 0 18 is_stmt 0                ; candidate.py:0:18
	sl_mov_b32 s2, s26
	.loc	1 42 18                         ; candidate.py:42:18
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[4:5], 0x0, 0x0, 0x800, 0x1
	sl_jump BB0_2
BB0_5:                                  ; %._crit_edge.loopexit
	.loc	1 47 48 is_stmt 1               ; candidate.py:47:48
	ml_cvt_bf16_f32  v0, v0
	ml_cvt_bf16_f32  v1, v1
	ml_cvt_bf16_f32  v2, v2
	ml_cvt_bf16_f32  v3, v3
BB0_6:                                  ; %._crit_edge
	.loc	1 32 25                         ; candidate.py:32:25
	sl_srl_b32 {s0, wcr}, s28, 0x4
	ml_bfe2_b32 v5, v4, 0x63
	.loc	1 32 13 is_stmt 0               ; candidate.py:32:13
	sl_add_i32 s0, s23, s0
	ml_add_i32 v8, s0, v5
	ml_add_i32 v9, v8, 0x8
	.loc	1 47 26 is_stmt 1               ; candidate.py:47:26
	ml_mul_u64_u32 v[5:6], s22, v8
	.loc	1 33 25                         ; candidate.py:33:25
	sl_srl_b32 {s0, wcr}, s10, 0x2
	sl_and_b32 {s0, wcr}, s0, 0x30
	.loc	1 33 13 is_stmt 0               ; candidate.py:33:13
	sl_add_i32 s0, s11, s0
	.loc	1 47 26 is_stmt 1               ; candidate.py:47:26
	ml_mul_u64_u32 v[6:7], s22, v9
	.loc	1 47 48 is_stmt 0               ; candidate.py:47:48
	sl_mov_b32 s6, 0x1000504
	sl_mov_b32 s10, 0x2010200
	.loc	1 33 25 is_stmt 1               ; candidate.py:33:25
	ml_shl_b32 v4, v4, 0x1
	ml_and_b32 v7, v4, 0xe
	.loc	1 33 13 is_stmt 0               ; candidate.py:33:13
	ml_add_i32 v7, s0, v7
	.loc	1 46 21 is_stmt 1               ; candidate.py:46:21
	ml_cmp_gt_i32 tcr, s18, v8
	.loc	1 47 15                         ; candidate.py:47:15
	ml_sra_b32 v8, v5, 0x1f
	ml_shl_b32 v8, v8, 0x1
	ml_srl_b32 v10, v5, 0x1f
	.loc	1 46 21                         ; candidate.py:46:21
	sl_mov_b64 s[0:1], tcr
	ml_cmp_gt_i32 tcr, s18, v9
	.loc	1 47 15                         ; candidate.py:47:15
	ml_shl_b32 v9, v5, 0x1
	ml_or_b32 v8, v8, v10
	ml_mov_b32 v10, s17
	.loc	1 46 21                         ; candidate.py:46:21
	sl_mov_b64 s[2:3], tcr
	.loc	1 46 36 is_stmt 0               ; candidate.py:46:36
	ml_cmp_gt_i32 tcr, s19, v7
	.loc	1 47 30 is_stmt 1               ; candidate.py:47:30
	ml_shl_b32 v11, v7, 0x1
	.loc	1 47 48 is_stmt 0               ; candidate.py:47:48
	ml_byte_permute_b32 v0, v1, v0, s6
	ml_byte_permute_b32 v1, v3, v2, s6
	.loc	1 46 36 is_stmt 1               ; candidate.py:46:36
	sl_mov_b64 s[4:5], tcr
	.loc	1 47 15                         ; candidate.py:47:15
	ml_addo_u32 {v9, tcr}, s16, v9
	.loc	1 47 48 is_stmt 0               ; candidate.py:47:48
	ml_and_b32 v2, tid, 0x1
	ml_mov_b32 v3, 0x5410
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[6:7], wcr}, s[0:1], s[4:5]
	.loc	1 47 15                         ; candidate.py:47:15
	ml_addc_i32 v8, v10, v8, tcr
	.loc	1 47 30 is_stmt 0               ; candidate.py:47:30
	ml_sra_b32 v10, v7, 0x1f
	ml_addo_u32 {v9, tcr}, v11, v9
	ml_shl_b32 v10, v10, 0x1
	ml_srl_b32 v7, v7, 0x1f
	ml_or_b32 v7, v10, v7
	ml_addc_i32 v7, v8, v7, tcr
	.loc	1 47 48                         ; candidate.py:47:48
	ml_cmp_eq_u32 tcr, v2, 0x0
	ml_mov_b32 v2, 0x7632
	ml_csel_b32 v8, v3, v2, tcr
	ml_csel_b32 v10, v2, v3, tcr
	ml_byte_permute_b32 v8, v8, v8, s10
	ml_pk_shl_b16 v8, v8, 0x40004
	ml_pk_srl_b8 v8, v8, 0x40004
	ml_byte_permute_b32 v8, v0, v1, v8
	ml_byte_permute_b32 v10, v10, v10, s10
	ml_pk_shl_b16 v10, v10, 0x40004
	ml_bfe2_b32 v11, tid, 0x25
	ml_anyop3_b32 v4, 62, v4, v11, 0xfffffff8
	ml_slb_shuffle_rtn_b32 v8, v8, v4
	ml_pk_srl_b8 v10, v10, 0x40004
	ml_byte_permute_b32 v0, v0, v1, v10
	ml_xor_b32 v1, v4, 0x1
	ml_slb_shuffle_rtn_b32 v0, v0, v1
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[4:5], wcr}, s[4:5], s[2:3]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_and_b32 v1, tid, 0x20
	ml_cmp_eq_u32 tcr, v1, 0x0
	ml_mov_b32 v1, 0x1054
	ml_csel_b32 v1, v3, v1, tcr
	ml_mov_b32 v3, 0x3276
	ml_csel_b32 v2, v2, v3, tcr
	ml_byte_permute_b32 v1, v1, v1, s10
	ml_pk_shl_b16 v1, v1, 0x40004
	ml_pk_srl_b8 v1, v1, 0x40004
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_mov_v2s_b32 s0, v9, 0x0
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v2, v2, v2, s10
	ml_pk_shl_b16 v2, v2, 0x40004
	.loc	1 47 61                         ; candidate.py:47:61
	ml_mov_v2s_b32 s1, v7, 0x0
	ml_mov_b32 v3, s0
	ml_sub_i32 v3, v9, v3
	sl_mov_b32 s3, s26
	ml_sub_i32 v4, v6, v5
	ml_shl_b32 v4, v4, 0x1
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v1, v8, v0, v1
	.loc	1 47 61                         ; candidate.py:47:61
	ml_mov_v2s_b32 s2, v4, 0x0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v1, s[0:3], signed v3, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_pk_srl_b8 v1, v2, 0x40004
	ml_byte_permute_b32 v0, v8, v0, v1
	.loc	1 47 61                         ; candidate.py:47:61
	ml_add_i32 v1, s2, v3
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v0, s[0:3], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 4                          ; candidate.py:47:4
	sl_eop 
.Ltmp15:
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	nonly_other_rows_linear.kd
	.type	nonly_other_rows_linear.kd,@object
	.size	nonly_other_rows_linear.kd, 64
nonly_other_rows_linear.kd:
	.asciz	"\000\000\000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	nonly_other_rows_linear@rel64-nonly_other_rows_linear.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	536836
	.asciz	"\003\000\224\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	nonly_other_rows_linear, .Lfunc_end0-nonly_other_rows_linear
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 2984
; NumSgprs: 36
; NumVgprs: 18
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 4
; VGPRBlocks: 4
; NumSGPRsForWarpsPerNU: 32
; NumVGPRsForWarpsPerNR: 18
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
	.long	241                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0xea DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"candidate.py"                  ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/workspace/experiments/minicpm-s2/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/source" ; DW_AT_comp_dir
	.byte	0
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.byte	2                               ; Abbrev [2] 0xa0:0x1a DW_TAG_subprogram
	.ascii	"nonly_other_rows_linear"       ; DW_AT_name
	.byte	0
	.byte	1                               ; DW_AT_inline
	.byte	3                               ; Abbrev [3] 0xba:0x3a DW_TAG_subprogram
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.long	160                             ; DW_AT_abstract_origin
	.byte	4                               ; Abbrev [4] 0xcf:0xc DW_TAG_inlined_subroutine
	.long	160                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges0                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	27                              ; DW_AT_call_line
	.byte	21                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0xdb:0xc DW_TAG_inlined_subroutine
	.long	160                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges1                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	27                              ; DW_AT_call_line
	.byte	42                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0xe7:0xc DW_TAG_inlined_subroutine
	.long	160                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges2                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	41                              ; DW_AT_call_line
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
	.quad	.Ltmp11-.Lfunc_begin0
	.quad	.Ltmp12-.Lfunc_begin0
	.quad	.Ltmp13-.Lfunc_begin0
	.quad	.Ltmp14-.Lfunc_begin0
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
    .name:           nonly_other_rows_linear
    .private_segment_fixed_size: 0
    .sgpr_count:     36
    .sgpr_spill_count: 0
    .symbol:         nonly_other_rows_linear.kd
    .vgpr_count:     18
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
