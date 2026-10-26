	.text
	.globl	nonly_other_rows_linear         ; -- Begin function nonly_other_rows_linear
	.p2align	3
	.type	nonly_other_rows_linear,@function
	.iluvatar_kernel nonly_other_rows_linear
nonly_other_rows_linear:                ; @nonly_other_rows_linear
.Lfunc_begin0:
	.file	1 "/workspace/experiments/minicpm-s2/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/source" "candidate.py"
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
		granulated_workitem_vgpr_count = 13
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
		warp_sgpr_count = 40
		workitem_vgpr_count = 56
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
	ml_vrf_init_u32 v48, tcr
.Ltmp0:
	.file	2 "/usr/local/lib/python3.12/site-packages/triton/language" "standard.py"
	.loc	2 65 17 prologue_end            ; standard.py:65:17 @[ candidate.py:27:42 ]
	sl_lsa_load_b32x16 s[20:35], s[4:5], noreg, #0, ca
.Ltmp1:
	.loc	2 65 17 is_stmt 0               ; standard.py:65:17 @[ candidate.py:27:21 ]
	sl_wait smcnt(0)
	sl_add_i32 s0, s26, 0xff
.Ltmp2:
	.loc	2 65 17                         ; standard.py:65:17 @[ candidate.py:27:42 ]
	sl_add_i32 s1, s27, 0x7f
.Ltmp3:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:21 ]
	sl_sra_b32 {s2, wcr}, s0, 0x1f
.Ltmp4:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:42 ]
	sl_sra_b32 {s3, wcr}, s1, 0x1f
.Ltmp5:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:21 ]
	sl_srl_b32 {s2, wcr}, s2, 0x18
.Ltmp6:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:42 ]
	sl_srl_b32 {s3, wcr}, s3, 0x19
.Ltmp7:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:21 ]
	sl_add_i32 s0, s0, s2
.Ltmp8:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:42 ]
	sl_add_i32 s1, s1, s3
.Ltmp9:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:21 ]
	sl_sra_b32 {s7, wcr}, s0, 0x8
.Ltmp10:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:27:42 ]
	sl_sra_b32 {s0, wcr}, s1, 0x7
.Ltmp11:
	.loc	1 28 33 is_stmt 1               ; candidate.py:28:33
	sl_sra_b32 {s11, wcr}, s1, 0x1f
	sl_shl_b32 {s14, wcr}, s0, 0x3
	sl_sub_bi_u32 s0, s8, s8, wcr
	sl_abs_i32 s1, s14
	ml_cvt_f32_u32  v0, s1
	sl_reg_read s2, hwreg(HW_REG_MODE)
	ml_rcp_f32 v0, v0
	sl_or_b32 {s3, wcr}, s2, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s3
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s2
	ml_mov_v2s_b32 s4, v0, 0x0
	sl_mov_b32 s34, 0xffffffff
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
	sl_sub_bi_u64 s[12:13], s[8:9], s[8:9], wcr
	sl_and_b64 {s[4:5], wcr}, s[4:5], s[12:13]
	sl_or_b32 {s4, wcr}, s4, s5
	sl_csel_b32 s2, s34, 0x0, wcr
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
	sl_mull_u32 s12, s11, 0x8
	.loc	1 29 26 is_stmt 0               ; candidate.py:29:26
	sl_sub_i32 s0, s7, s12
	.loc	1 29 37                         ; candidate.py:29:37
	sl_min_i32 s7, s0, 0x8
	.loc	1 30 22 is_stmt 1               ; candidate.py:30:22
	sl_abs_i32 s13, s7
	ml_cvt_f32_u32  v0, s13
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
	sl_mul_u64_u32 s[2:3], s1, s13
	sl_neg_i32 s4, s2
	sl_cmp_eq_u32 wcr, s3, 0x0
	sl_csel_b32 s2, s4, s2, wcr
	sl_mul_u64_u32 s[2:3], s2, s1
	sl_add_i32 s2, s1, s3
	sl_sub_i32 s1, s1, s3
	sl_csel_b32 s15, s2, s1, wcr
	sl_mul_u64_u32 s[2:3], s15, s6
	sl_mull_u32 s1, s3, s13
	sl_sub_i32 s16, s6, s1
	sl_cmp_ge_u32 wcr, s16, s13
	sl_sub_bi_u64 s[2:3], s[8:9], s[8:9], wcr
	sl_cmp_ge_u32 wcr, s6, s1
	sl_sub_bi_u32 s1, s8, s8, wcr
	sl_sub_bi_u64 s[4:5], s[8:9], s[8:9], wcr
	sl_and_b64 {s[2:3], wcr}, s[2:3], s[4:5]
	sl_or_b32 {s2, wcr}, s2, s3
	sl_csel_b32 s2, s34, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_sub_i32 s2, s16, s13
	sl_add_i32 s3, s16, s13
	sl_csel_b32 s2, s16, s2, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s2, s3, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s1, s34, s1, wcr
	.loc	1 30 18 is_stmt 0               ; candidate.py:30:18
	sl_add_i32 s12, s12, s1
	.loc	1 31 12 is_stmt 1               ; candidate.py:31:12
	sl_mull_u32 s1, s11, s14
	sl_sub_i32 s1, s6, s1
	.loc	1 31 20 is_stmt 0               ; candidate.py:31:20
	sl_xor_b32 {s2, wcr}, s1, s7
	sl_sra_b32 {s11, wcr}, s2, 0x1f
	sl_abs_i32 s1, s1
	sl_mul_u64_u32 s[2:3], s15, s1
	sl_mull_u32 s2, s3, s13
	sl_sub_i32 s4, s1, s2
	sl_cmp_ge_u32 wcr, s4, s13
	sl_sub_bi_u64 s[4:5], s[8:9], s[8:9], wcr
	sl_cmp_ge_u32 wcr, s1, s2
	sl_sub_bi_u32 s1, s8, s8, wcr
	sl_sub_bi_u64 s[6:7], s[8:9], s[8:9], wcr
	sl_and_b64 {s[4:5], wcr}, s[4:5], s[6:7]
	sl_or_b32 {s4, wcr}, s4, s5
	sl_csel_b32 s2, s34, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_add_i32 s2, s3, 0x1
	sl_add_i32 s4, s3, 0xffffffff
	sl_csel_b32 s2, s3, s2, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s2, s4, wcr
	sl_xor_b32 {s1, wcr}, s1, s11
	sl_sub_i32 s1, s1, s11
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s34, s1, wcr
	.loc	1 32 10 is_stmt 1               ; candidate.py:32:10
	sl_mull_u32 s11, s12, 0x100
	.loc	1 34 44                         ; candidate.py:34:44
	sl_abs_i32 s6, s26
	ml_cvt_f32_u32  v0, s6
	.loc	1 32 25                         ; candidate.py:32:25
	sl_bfe2_b32 s13, tcr_lo, 0x86
	.loc	1 34 44                         ; candidate.py:34:44
	ml_rcp_f32 v0, v0
	.loc	1 33 10                         ; candidate.py:33:10
	sl_mull_u32 s12, s0, 0x80
	.loc	1 34 44                         ; candidate.py:34:44
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_sra_b32 {s7, wcr}, s11, 0x1f
	sl_abs_i32 s4, s11
	sl_or_b32 {s1, wcr}, s0, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s0
	ml_mov_v2s_b32 s2, v0, 0x0
	.loc	1 42 18                         ; candidate.py:42:18
	sl_mull_u32 s35, s29, 0x2
	sl_mull_u32 s14, s13, 0x400
	sl_mov_b32 s15, 0x0
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
	sl_csel_b32 s2, s34, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_sub_i32 s2, s1, s6
	sl_add_i32 s3, s1, s6
	sl_csel_b32 s1, s1, s2, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s1, s3, wcr
	sl_xor_b32 {s0, wcr}, s0, s7
	sl_sub_i32 s0, s0, s7
	sl_cmp_ne_u32 wcr, s26, 0x0
	sl_csel_b32 s0, s0, 0xffffffff, wcr
	.loc	1 36 21                         ; candidate.py:36:21
	sl_mull_u32 s0, s0, s29
	.loc	1 36 9 is_stmt 0                ; candidate.py:36:9
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[32:33], s[20:21], s[0:1]
	.loc	1 42 18 is_stmt 1               ; candidate.py:42:18
	sl_mull_u32 s0, s13, s29
	sl_mull_u32 s4, s0, 0x20
	sl_mov_b32 s5, s14
	sl_sme_load_16x1b64_rowxfb16 s[32:35], s[4:5], 0x0, 0x0, 0x0, 0x1
.Ltmp12:
	.loc	2 65 17                         ; standard.py:65:17 @[ candidate.py:41:35 ]
	sl_add_i32 s0, s28, 0x1f
.Ltmp13:
	.loc	1 41 25                         ; candidate.py:41:25
	sl_cmp_gt_i32 wcr, s0, 0x1f
	ml_mov_b32 v39, 0x0
	ml_mov_b32 v40, 0x0
	ml_mov_b32 v41, 0x0
	ml_mov_b32 v42, 0x0
	ml_mov_b32 v35, 0x0
	ml_mov_b32 v36, 0x0
	ml_mov_b32 v37, 0x0
	ml_mov_b32 v38, 0x0
	ml_mov_b32 v32, 0x0
	ml_mov_b32 v33, 0x0
	ml_mov_b32 v18, 0x0
	ml_mov_b32 v34, 0x0
	ml_mov_b32 v17, 0x0
	ml_mov_b32 v19, 0x0
	ml_mov_b32 v24, 0x0
	ml_mov_b32 v25, 0x0
	ml_mov_b32 v8, 0x0
	ml_mov_b32 v10, 0x0
	ml_mov_b32 v11, 0x0
	ml_mov_b32 v16, 0x0
	ml_mov_b32 v9, 0x0
	ml_mov_b32 v12, 0x0
	ml_mov_b32 v13, 0x0
	ml_mov_b32 v14, 0x0
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v2, 0x0
	ml_mov_b32 v4, 0x0
	ml_mov_b32 v6, 0x0
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v3, 0x0
	ml_mov_b32 v5, 0x0
	ml_mov_b32 v7, 0x0
	sl_cbr_wcrz BB0_6, wcr
; %bb.1:                                ; %.lr.ph
	.loc	1 0 0 is_stmt 0                 ; candidate.py:0
	sl_srl_b32 {s2, wcr}, s10, 0x6
.Ltmp14:
	.loc	2 65 30 is_stmt 1               ; standard.py:65:30 @[ candidate.py:41:35 ]
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_srl_b32 {s1, wcr}, s1, 0x1b
	sl_add_i32 s0, s0, s1
	sl_sra_b32 {s16, wcr}, s0, 0x5
.Ltmp15:
	.loc	1 39 19                         ; candidate.py:39:19
	sl_srl_b32 {s0, wcr}, s12, 0x7
	.loc	1 39 25 is_stmt 0               ; candidate.py:39:25
	sl_mull_u32 s0, s28, s0
	sl_mull_u32 s0, s0, 0x80
	.loc	1 39 9                          ; candidate.py:39:9
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	ml_shl_b32 v0, v48, 0x2
	ml_and_b32 v49, v0, 0xcfc
	sl_srl_b32 {s3, wcr}, s13, 0x1
	sl_mull_u32 s5, s3, 0x40
	sl_mull_u32 s2, s2, 0x1000
	sl_and_b32 {s2, wcr}, s2, 0x1000
	sl_add_i32 s6, s5, s2
	sl_mull_u32 s3, s3, 0x400
	sl_add_i32 s2, s2, s3
	sl_add_i32 s7, s2, 0x8000
	sl_and_b32 {s2, wcr}, s10, 0x40
	sl_mov_b32 s2, 0x280
	sl_csel_b32 s2, s2, 0x0, wcr
	sl_mull_u32 s3, s10, 0x8
	sl_and_b32 {s17, wcr}, s3, 0x400
	ml_mov_b32 v1, 0xfc
	ml_anyop3_b32 v50, s2, v0, v1, 0x6a
	.loc	1 41 25 is_stmt 1               ; candidate.py:41:25
	sl_add_i64 s[32:33], s[32:33], 0x40
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[0:1], s[22:23], s[0:1]
	ml_mov_b32 v0, 0x0
	ml_xor_b32 v51, v49, 0x80
	sl_mov_b32 s3, 0x100
	sl_mov_b32 s18, s34
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v26, 0x0
	ml_mov_b32 v27, 0x0
	ml_mov_b32 v15, 0x0
	ml_mov_b32 v20, 0x0
	ml_mov_b32 v21, 0x0
	ml_mov_b32 v22, 0x0
	ml_mov_b32 v23, 0x0
	ml_mov_b32 v28, 0x0
	ml_mov_b32 v29, 0x0
	ml_mov_b32 v30, 0x0
	ml_mov_b32 v31, 0x0
	sl_jump BB0_3
BB0_2:                                  ;   in Loop: Header=BB0_3 Depth=1
	.loc	1 42 32                         ; candidate.py:42:32
	sl_wait lmcnt(0) g2scnt(0)
	sl_barrier 
	sl_add_i32 s2, s17, 0x8000
	ml_slb_load_b32x1  v52, v50, s2, #0, null
	sl_add_i32 s19, s17, 0x8800
	.loc	1 41 25                         ; candidate.py:41:25
	sl_add_i32 s5, s15, 0x1
	sl_cmp_lt_i32 wcr, s5, 0x2
	.loc	1 42 32                         ; candidate.py:42:32
	ml_slb_load_b32x1  v53, v50, s2, #256, null
	.loc	1 41 25                         ; candidate.py:41:25
	sl_csel_b32 s15, s5, 0x0, wcr
	.loc	1 42 18                         ; candidate.py:42:18
	sl_mull_u32 s5, s15, 0x4000
	sl_add_i32 s5, s14, s5
	.loc	1 42 32 is_stmt 0               ; candidate.py:42:32
	ml_slb_load_b32x1  v54, v50, s19, #0, null
	.loc	1 42 18                         ; candidate.py:42:18
	sl_sme_load_16x1b64_rowxfb16 s[32:35], s[4:5], 0x0, 0x0, 0x0, 0x1
	.loc	1 42 32                         ; candidate.py:42:32
	sl_add_i32 s5, s17, 0x9000
	sl_add_i32 s20, s17, 0x9800
	ml_slb_load_b32x1  v55, v50, s19, #256, null
	.loc	1 41 25 is_stmt 1               ; candidate.py:41:25
	sl_add_i64 s[32:33], s[32:33], 0x40
	sl_add_i32 s16, s16, 0xffffffff
	sl_cmp_eq_u32 wcr, s16, 0x0
	sl_add_i64 s[0:1], s[0:1], 0x2000
	.loc	1 43 22                         ; candidate.py:43:22
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[32:33], v[52:53], v[0:3]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[32:33], v[54:55], v[4:7]
	.loc	1 42 32                         ; candidate.py:42:32
	ml_slb_load_b32x1  v32, v50, s5, #0, null
	ml_slb_load_b32x1  v33, v50, s5, #256, null
	.loc	1 43 22                         ; candidate.py:43:22
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[34:35], v[52:53], v[8:11]
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[34:35], v[54:55], v[12:15]
	.loc	1 42 32                         ; candidate.py:42:32
	ml_slb_load_b32x1  v34, v50, s20, #0, null
	ml_slb_load_b32x1  v35, v50, s20, #256, null
	.loc	1 43 22                         ; candidate.py:43:22
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[38:39], v[52:53], v[16:19]
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[38:39], v[54:55], v[20:23]
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[40:41], v[52:53], v[24:27]
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[40:41], v[54:55], v[28:31]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[36:37], v[32:33], v[0:3]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[36:37], v[34:35], v[4:7]
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[42:43], v[32:33], v[8:11]
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[42:43], v[34:35], v[12:15]
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[44:45], v[32:33], v[16:19]
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[44:45], v[34:35], v[20:23]
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[46:47], v[32:33], v[24:27]
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[46:47], v[34:35], v[28:31]
	.loc	1 41 25                         ; candidate.py:41:25
	sl_cbr_wcrnz BB0_5, wcr
BB0_3:                                  ; =>This Inner Loop Header: Depth=1
	sl_add_i32 s2, s18, 0x1
	sl_cmp_lt_i32 wcr, s2, 0x2
	sl_csel_b32 s18, s2, 0x0, wcr
	.loc	1 42 18                         ; candidate.py:42:18
	sl_wait g2scnt(0)
	sl_barrier_req 0x0
	sl_barrier_wait 0x0
	sl_mull_u32 s2, s18, 0x4000
	ml_slb_load_b32x1  v32, v49, s2, #0, null
	sl_add_i32 s5, s2, 0x1000
	sl_add_i32 s19, s2, 0x2000
	sl_add_i32 s20, s2, 0x3000
	ml_slb_load_b32x1  v33, v49, s2, #256, null
	sl_cmp_lt_u32 wcr, s13, 0x8
	ml_slb_load_b32x1  v34, v49, s5, #0, null
	ml_slb_load_b32x1  v35, v49, s5, #256, null
	ml_slb_load_b32x1  v38, v49, s19, #0, null
	ml_slb_load_b32x1  v39, v49, s19, #256, null
	ml_slb_load_b32x1  v40, v49, s20, #0, null
	ml_slb_load_b32x1  v41, v49, s20, #256, null
	ml_slb_load_b32x1  v36, v51, s2, #512, null
	ml_slb_load_b32x1  v37, v51, s2, #768, null
	ml_slb_load_b32x1  v42, v51, s5, #512, null
	ml_slb_load_b32x1  v43, v51, s5, #768, null
	ml_slb_load_b32x1  v44, v51, s19, #512, null
	ml_slb_load_b32x1  v45, v51, s19, #768, null
	ml_slb_load_b32x1  v46, v51, s20, #512, null
	ml_slb_load_b32x1  v47, v51, s20, #768, null
	.loc	1 42 32 is_stmt 0               ; candidate.py:42:32
	sl_cbr_wcrz BB0_2, wcr
; %bb.4:                                ;   in Loop: Header=BB0_3 Depth=1
	.loc	1 0 32                          ; candidate.py:0:32
	sl_mov_b32 s2, s34
	.loc	1 42 32                         ; candidate.py:42:32
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[6:7], 0x0, 0x0, 0x0, 0x1
	sl_jump BB0_2
BB0_5:                                  ; %._crit_edge.loopexit
	.loc	1 47 48 is_stmt 1               ; candidate.py:47:48
	ml_cvt_bf16_f32  v39, v0
	ml_cvt_bf16_f32  v40, v1
	ml_cvt_bf16_f32  v41, v2
	ml_cvt_bf16_f32  v42, v3
	ml_cvt_bf16_f32  v35, v8
	ml_cvt_bf16_f32  v36, v9
	ml_cvt_bf16_f32  v37, v10
	ml_cvt_bf16_f32  v38, v11
	ml_cvt_bf16_f32  v32, v16
	ml_cvt_bf16_f32  v33, v17
	ml_cvt_bf16_f32  v18, v18
	ml_cvt_bf16_f32  v34, v19
	ml_cvt_bf16_f32  v17, v24
	ml_cvt_bf16_f32  v19, v25
	ml_cvt_bf16_f32  v24, v26
	ml_cvt_bf16_f32  v25, v27
	ml_cvt_bf16_f32  v8, v4
	ml_cvt_bf16_f32  v10, v5
	ml_cvt_bf16_f32  v11, v6
	ml_cvt_bf16_f32  v16, v7
	ml_cvt_bf16_f32  v9, v12
	ml_cvt_bf16_f32  v12, v13
	ml_cvt_bf16_f32  v13, v14
	ml_cvt_bf16_f32  v14, v15
	ml_cvt_bf16_f32  v0, v20
	ml_cvt_bf16_f32  v2, v21
	ml_cvt_bf16_f32  v4, v22
	ml_cvt_bf16_f32  v6, v23
	ml_cvt_bf16_f32  v1, v28
	ml_cvt_bf16_f32  v3, v29
	ml_cvt_bf16_f32  v5, v30
	ml_cvt_bf16_f32  v7, v31
BB0_6:                                  ; %._crit_edge
	.loc	1 33 25                         ; candidate.py:33:25
	ml_shl_b32 v15, v48, 0x1
	ml_and_b32 v20, v15, 0xe
	sl_srl_b32 {s0, wcr}, s10, 0x2
	sl_and_b32 {s0, wcr}, s0, 0x30
	.loc	1 33 13 is_stmt 0               ; candidate.py:33:13
	sl_add_i32 s0, s12, s0
	ml_add_i32 v43, s0, v20
	ml_add_i32 v44, v43, 0x40
	.loc	1 32 25 is_stmt 1               ; candidate.py:32:25
	ml_bfe2_b32 v20, v48, 0x63
	sl_srl_b32 {s0, wcr}, s10, 0x4
	sl_and_b32 {s0, wcr}, s0, 0x30
	.loc	1 32 13 is_stmt 0               ; candidate.py:32:13
	sl_add_i32 s0, s11, s0
	ml_add_i32 v30, s0, v20
	ml_add_i32 v31, v30, 0xc8
	ml_add_i32 v45, v30, 0xc0
	ml_add_i32 v46, v30, 0x88
	ml_add_i32 v47, v30, 0x80
	ml_add_i32 v48, v30, 0x48
	ml_add_i32 v49, v30, 0x40
	ml_add_i32 v50, v30, 0x8
	.loc	1 41 25 is_stmt 1               ; candidate.py:41:25
	sl_wait g2scnt(0)
	sl_barrier 
	.loc	1 47 26                         ; candidate.py:47:26
	ml_mul_u64_u32 v[20:21], s30, v30
	.loc	1 47 48 is_stmt 0               ; candidate.py:47:48
	sl_mov_b32 s22, 0x1000504
	sl_mov_b32 s23, 0x2010200
	.loc	1 47 26                         ; candidate.py:47:26
	ml_mul_u64_u32 v[21:22], s30, v50
	ml_mul_u64_u32 v[22:23], s30, v49
	ml_mul_u64_u32 v[26:27], s30, v48
	ml_mul_u64_u32 v[27:28], s30, v47
	ml_mul_u64_u32 v[28:29], s30, v46
	.loc	1 46 21 is_stmt 1               ; candidate.py:46:21
	ml_cmp_gt_i32 tcr, s26, v30
	.loc	1 47 26                         ; candidate.py:47:26
	ml_mul_u64_u32 v[29:30], s30, v45
	.loc	1 46 21                         ; candidate.py:46:21
	sl_mov_b64 s[6:7], tcr
	ml_cmp_gt_i32 tcr, s26, v50
	.loc	1 47 15                         ; candidate.py:47:15
	ml_sra_b32 v23, v20, 0x1f
	ml_shl_b32 v30, v20, 0x1
	ml_shl_b32 v23, v23, 0x1
	.loc	1 46 21                         ; candidate.py:46:21
	sl_mov_b64 s[18:19], tcr
	ml_cmp_gt_i32 tcr, s26, v49
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v39, v40, v39, s22
	ml_byte_permute_b32 v40, v42, v41, s22
	ml_and_b32 v41, tid, 0x1
	.loc	1 46 21                         ; candidate.py:46:21
	sl_mov_b64 s[16:17], tcr
	ml_cmp_gt_i32 tcr, s26, v48
	ml_mov_b32 v42, 0x5410
	.loc	1 47 48                         ; candidate.py:47:48
	ml_and_b32 v48, tid, 0x20
	.loc	1 46 21                         ; candidate.py:46:21
	sl_mov_b64 s[14:15], tcr
	ml_cmp_gt_i32 tcr, s26, v47
	.loc	1 47 48                         ; candidate.py:47:48
	ml_bfe2_b32 v47, tid, 0x25
	ml_anyop3_b32 v15, 62, v15, v47, 0xfffffff8
	.loc	1 46 21                         ; candidate.py:46:21
	sl_mov_b64 s[12:13], tcr
	ml_cmp_gt_i32 tcr, s26, v46
	.loc	1 47 30                         ; candidate.py:47:30
	ml_shl_b32 v46, v43, 0x1
	.loc	1 46 21                         ; candidate.py:46:21
	sl_mov_b64 s[10:11], tcr
	ml_cmp_gt_i32 tcr, s26, v45
	.loc	1 47 15                         ; candidate.py:47:15
	ml_srl_b32 v45, v20, 0x1f
	ml_or_b32 v23, v23, v45
	ml_mov_b32 v45, s25
	.loc	1 46 21                         ; candidate.py:46:21
	sl_mov_b64 s[2:3], tcr
	ml_cmp_gt_i32 tcr, s26, v31
	sl_mov_b64 s[0:1], tcr
	.loc	1 46 36 is_stmt 0               ; candidate.py:46:36
	ml_cmp_gt_i32 tcr, s27, v43
	sl_mov_b64 s[20:21], tcr
	ml_cmp_gt_i32 tcr, s27, v44
	.loc	1 46 25                         ; candidate.py:46:25
	sl_and_b64 {s[28:29], wcr}, s[6:7], s[20:21]
	.loc	1 47 61 is_stmt 1               ; candidate.py:47:61
	sl_mov_b32 s27, s34
	.loc	1 46 36                         ; candidate.py:46:36
	sl_mov_b64 s[4:5], tcr
	.loc	1 47 15                         ; candidate.py:47:15
	ml_addo_u32 {v30, tcr}, s24, v30
	ml_addc_i32 v23, v45, v23, tcr
	.loc	1 47 30 is_stmt 0               ; candidate.py:47:30
	ml_sra_b32 v45, v43, 0x1f
	ml_addo_u32 {v30, tcr}, v46, v30
	ml_shl_b32 v45, v45, 0x1
	ml_srl_b32 v46, v43, 0x1f
	ml_or_b32 v45, v45, v46
	ml_addc_i32 v23, v23, v45, tcr
	.loc	1 47 48                         ; candidate.py:47:48
	ml_cmp_eq_u32 tcr, v41, 0x0
	ml_mov_b32 v41, 0x7632
	ml_csel_b32 v45, v42, v41, tcr
	ml_byte_permute_b32 v45, v45, v45, s23
	ml_pk_shl_b16 v45, v45, 0x40004
	ml_pk_srl_b8 v45, v45, 0x40004
	ml_byte_permute_b32 v46, v39, v40, v45
	ml_slb_shuffle_rtn_b32 v46, v46, v15
	ml_csel_b32 v47, v41, v42, tcr
	ml_byte_permute_b32 v47, v47, v47, s23
	ml_pk_shl_b16 v47, v47, 0x40004
	ml_pk_srl_b8 v47, v47, 0x40004
	ml_byte_permute_b32 v39, v39, v40, v47
	ml_xor_b32 v40, v15, 0x1
	ml_slb_shuffle_rtn_b32 v39, v39, v40
	ml_cmp_eq_u32 tcr, v48, 0x0
	ml_mov_b32 v48, 0x1054
	ml_csel_b32 v42, v42, v48, tcr
	ml_byte_permute_b32 v42, v42, v42, s23
	.loc	1 47 61                         ; candidate.py:47:61
	ml_mov_v2s_b32 s24, v30, 0x0
	.loc	1 47 48                         ; candidate.py:47:48
	ml_pk_shl_b16 v42, v42, 0x40004
	ml_pk_srl_b8 v42, v42, 0x40004
	.loc	1 47 61                         ; candidate.py:47:61
	ml_mov_v2s_b32 s25, v23, 0x0
	ml_mov_b32 v23, s24
	ml_sub_i32 v23, v30, v23
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v30, v46, v39, v42
	.loc	1 47 61                         ; candidate.py:47:61
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[28:29], tmsk
	ml_lsa_store_dword v30, s[24:27], signed v23, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v30, v36, v35, s22
	ml_byte_permute_b32 v35, v38, v37, s22
	ml_byte_permute_b32 v36, v30, v35, v45
	ml_slb_shuffle_rtn_b32 v36, v36, v15
	ml_byte_permute_b32 v30, v30, v35, v47
	ml_mov_b32 v35, 0x3276
	ml_csel_b32 v35, v41, v35, tcr
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[28:29], wcr}, s[20:21], s[18:19]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_slb_shuffle_rtn_b32 v37, v30, v40
	ml_byte_permute_b32 v30, v35, v35, s23
	ml_pk_shl_b16 v30, v30, 0x40004
	ml_pk_srl_b8 v35, v30, 0x40004
	ml_byte_permute_b32 v30, v46, v39, v35
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_sub_i32 v38, v21, v20
	ml_shl_b32 v38, v38, 0x1
	ml_mov_v2s_b32 s23, v38, 0x0
	ml_sub_i32 v38, v22, v20
	ml_shl_b32 v38, v38, 0x1
	ml_mov_v2s_b32 s26, v38, 0x0
	ml_add_i32 v38, s23, v23
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[28:29], tmsk
	ml_lsa_store_dword v30, s[24:27], signed v38, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[28:29], wcr}, s[20:21], s[16:17]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v30, v36, v37, v42
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v38, s26, v23
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[28:29], tmsk
	ml_lsa_store_dword v30, s[24:27], signed v38, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v32, v33, v32, s22
	ml_byte_permute_b32 v18, v34, v18, s22
	ml_byte_permute_b32 v33, v32, v18, v45
	.loc	1 47 26                         ; candidate.py:47:26
	ml_mul_u64_u32 v[30:31], s30, v31
	.loc	1 47 48                         ; candidate.py:47:48
	ml_slb_shuffle_rtn_b32 v31, v33, v15
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[28:29], wcr}, s[20:21], s[14:15]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v18, v32, v18, v47
	ml_slb_shuffle_rtn_b32 v18, v18, v40
	ml_byte_permute_b32 v17, v19, v17, s22
	ml_byte_permute_b32 v19, v25, v24, s22
	ml_byte_permute_b32 v24, v17, v19, v45
	ml_slb_shuffle_rtn_b32 v24, v24, v15
	ml_byte_permute_b32 v17, v17, v19, v47
	ml_byte_permute_b32 v19, v36, v37, v35
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_sub_i32 v25, v26, v20
	.loc	1 47 48                         ; candidate.py:47:48
	ml_slb_shuffle_rtn_b32 v17, v17, v40
	.loc	1 47 61                         ; candidate.py:47:61
	ml_shl_b32 v25, v25, 0x1
	ml_mov_v2s_b32 s23, v25, 0x0
	ml_sub_i32 v25, v27, v20
	ml_shl_b32 v25, v25, 0x1
	ml_mov_v2s_b32 s26, v25, 0x0
	ml_add_i32 v25, s23, v23
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[28:29], tmsk
	ml_lsa_store_dword v19, s[24:27], signed v25, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[28:29], wcr}, s[20:21], s[12:13]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v19, v31, v18, v42
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v25, s26, v23
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[28:29], tmsk
	ml_lsa_store_dword v19, s[24:27], signed v25, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	ml_sub_i32 v19, v28, v20
	ml_shl_b32 v19, v19, 0x1
	ml_mov_v2s_b32 s23, v19, 0x0
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[28:29], wcr}, s[20:21], s[10:11]
	sl_and_b64 {s[30:31], wcr}, s[20:21], s[2:3]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v18, v31, v18, v35
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v19, s23, v23
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[28:29], tmsk
	ml_lsa_store_dword v18, s[24:27], signed v19, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v18, v24, v17, v42
	.loc	1 47 61                         ; candidate.py:47:61
	ml_sub_i32 v19, v29, v20
	ml_shl_b32 v19, v19, 0x1
	ml_mov_v2s_b32 s23, v19, 0x0
	ml_sub_i32 v19, v30, v20
	ml_shl_b32 v19, v19, 0x1
	ml_mov_v2s_b32 s26, v19, 0x0
	ml_add_i32 v19, s23, v23
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[30:31], tmsk
	ml_lsa_store_dword v18, s[24:27], signed v19, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[20:21], wcr}, s[20:21], s[0:1]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v17, v24, v17, v35
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v18, s26, v23
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[20:21], tmsk
	ml_lsa_store_dword v17, s[24:27], signed v18, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v8, v10, v8, s22
	ml_byte_permute_b32 v10, v16, v11, s22
	ml_byte_permute_b32 v11, v8, v10, v45
	ml_slb_shuffle_rtn_b32 v11, v11, v15
	.loc	1 47 30                         ; candidate.py:47:30
	ml_add_i32 v16, v43, v20
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v8, v8, v10, v47
	ml_byte_permute_b32 v9, v12, v9, s22
	ml_slb_shuffle_rtn_b32 v8, v8, v40
	ml_byte_permute_b32 v10, v14, v13, s22
	ml_byte_permute_b32 v12, v9, v10, v45
	.loc	1 47 30                         ; candidate.py:47:30
	ml_add_i32 v13, v44, v21
	.loc	1 47 48                         ; candidate.py:47:48
	ml_slb_shuffle_rtn_b32 v12, v12, v15
	ml_byte_permute_b32 v9, v9, v10, v47
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[6:7], wcr}, s[6:7], s[4:5]
	.loc	1 47 61                         ; candidate.py:47:61
	ml_sub_i32 v10, v44, v43
	.loc	1 47 48 is_stmt 0               ; candidate.py:47:48
	ml_slb_shuffle_rtn_b32 v9, v9, v40
	.loc	1 47 61                         ; candidate.py:47:61
	ml_shl_b32 v10, v10, 0x1
	ml_mov_v2s_b32 s20, v10, 0x0
	ml_sub_i32 v13, v13, v16
	ml_shl_b32 v13, v13, 0x1
	ml_mov_v2s_b32 s21, v13, 0x0
	ml_add_i32 v13, s20, v23
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v10, v11, v8, v42
	.loc	1 47 61                         ; candidate.py:47:61
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v10, s[24:27], signed v13, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[6:7], wcr}, s[18:19], s[4:5]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v8, v11, v8, v35
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v10, s21, v23
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v8, s[24:27], signed v10, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 30                         ; candidate.py:47:30
	ml_add_i32 v8, v44, v22
	ml_add_i32 v10, v44, v26
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[6:7], wcr}, s[16:17], s[4:5]
	.loc	1 47 61                         ; candidate.py:47:61
	ml_sub_i32 v8, v8, v16
	ml_shl_b32 v8, v8, 0x1
	ml_mov_v2s_b32 s16, v8, 0x0
	.loc	1 47 48 is_stmt 0               ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v8, v12, v9, v42
	.loc	1 47 61                         ; candidate.py:47:61
	ml_sub_i32 v10, v10, v16
	ml_shl_b32 v10, v10, 0x1
	ml_mov_v2s_b32 s17, v10, 0x0
	ml_add_i32 v10, s16, v23
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v8, s[24:27], signed v10, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[6:7], wcr}, s[14:15], s[4:5]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v8, v12, v9, v35
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v9, s17, v23
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v8, s[24:27], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v0, v2, v0, s22
	ml_byte_permute_b32 v2, v6, v4, s22
	ml_byte_permute_b32 v4, v0, v2, v45
	ml_slb_shuffle_rtn_b32 v4, v4, v15
	.loc	1 47 30                         ; candidate.py:47:30
	ml_add_i32 v6, v44, v27
	ml_add_i32 v8, v44, v28
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v0, v0, v2, v47
	ml_slb_shuffle_rtn_b32 v0, v0, v40
	ml_byte_permute_b32 v1, v3, v1, s22
	ml_byte_permute_b32 v2, v7, v5, s22
	ml_byte_permute_b32 v3, v1, v2, v45
	ml_slb_shuffle_rtn_b32 v3, v3, v15
	.loc	1 47 30                         ; candidate.py:47:30
	ml_add_i32 v5, v44, v29
	ml_add_i32 v7, v44, v30
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v1, v1, v2, v47
	ml_slb_shuffle_rtn_b32 v1, v1, v40
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[6:7], wcr}, s[12:13], s[4:5]
	.loc	1 47 61                         ; candidate.py:47:61
	ml_sub_i32 v2, v6, v16
	ml_shl_b32 v2, v2, 0x1
	ml_mov_v2s_b32 s12, v2, 0x0
	ml_sub_i32 v6, v8, v16
	ml_shl_b32 v6, v6, 0x1
	ml_mov_v2s_b32 s13, v6, 0x0
	ml_add_i32 v6, s12, v23
	.loc	1 47 48 is_stmt 0               ; candidate.py:47:48
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v2, v4, v0, v42
	.loc	1 47 61                         ; candidate.py:47:61
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v2, s[24:27], signed v6, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[6:7], wcr}, s[10:11], s[4:5]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v0, v4, v0, v35
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v2, s13, v23
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v0, s[24:27], signed v2, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	ml_sub_i32 v0, v5, v16
	ml_shl_b32 v0, v0, 0x1
	ml_mov_v2s_b32 s6, v0, 0x0
	ml_sub_i32 v0, v7, v16
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[2:3], wcr}, s[2:3], s[4:5]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v2, v3, v1, v42
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_shl_b32 v0, v0, 0x1
	ml_mov_v2s_b32 s7, v0, 0x0
	ml_add_i32 v0, s6, v23
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[2:3], tmsk
	ml_lsa_store_dword v2, s[24:27], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v0, v3, v1, v35
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[0:1], wcr}, s[0:1], s[4:5]
	.loc	1 47 61                         ; candidate.py:47:61
	ml_add_i32 v1, s7, v23
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v0, s[24:27], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 4 is_stmt 0                ; candidate.py:47:4
	sl_eop 
.Ltmp16:
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
	.long	536845
	.asciz	"\003\000\224\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	nonly_other_rows_linear, .Lfunc_end0-nonly_other_rows_linear
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 5384
; NumSgprs: 40
; NumVgprs: 56
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 4
; VGPRBlocks: 13
; NumSGPRsForWarpsPerNU: 36
; NumVGPRsForWarpsPerNR: 56
; ReqNTIDx: 0
; MaxNTIDx: 0
; MinCTASm: 0
; ActiveWarp: 4
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
	.long	243                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0xec DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"candidate.py"                  ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/workspace/experiments/minicpm-s2/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/source" ; DW_AT_comp_dir
	.byte	0
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.byte	2                               ; Abbrev [2] 0xa2:0x1a DW_TAG_subprogram
	.ascii	"nonly_other_rows_linear"       ; DW_AT_name
	.byte	0
	.byte	1                               ; DW_AT_inline
	.byte	3                               ; Abbrev [3] 0xbc:0x3a DW_TAG_subprogram
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.long	162                             ; DW_AT_abstract_origin
	.byte	4                               ; Abbrev [4] 0xd1:0xc DW_TAG_inlined_subroutine
	.long	162                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges0                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	27                              ; DW_AT_call_line
	.byte	42                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0xdd:0xc DW_TAG_inlined_subroutine
	.long	162                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges1                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	27                              ; DW_AT_call_line
	.byte	21                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0xe9:0xc DW_TAG_inlined_subroutine
	.long	162                             ; DW_AT_abstract_origin
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
    .name:           nonly_other_rows_linear
    .private_segment_fixed_size: 0
    .sgpr_count:     40
    .sgpr_spill_count: 0
    .symbol:         nonly_other_rows_linear.kd
    .vgpr_count:     56
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
