	.text
	.globl	n256_linear                     ; -- Begin function n256_linear
	.p2align	3
	.type	n256_linear,@function
	.iluvatar_kernel n256_linear
n256_linear:                            ; @n256_linear
.Lfunc_begin0:
	.file	1 "/workspace/experiments/minicpm-s2/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/source" "candidate.py"
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
		granulated_workitem_vgpr_count = 23
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
		warp_sgpr_count = 44
		workitem_vgpr_count = 96
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
	ml_vrf_init_u32 v64, tcr
.Ltmp0:
	.file	2 "/usr/local/lib/python3.12/site-packages/triton/language" "standard.py"
	.loc	2 65 17 prologue_end            ; standard.py:65:17 @[ candidate.py:27:42 ]
	sl_lsa_load_b32x16 s[24:39], s[4:5], noreg, #0, ca
.Ltmp1:
	.loc	2 65 17 is_stmt 0               ; standard.py:65:17 @[ candidate.py:27:21 ]
	sl_wait smcnt(0)
	sl_add_i32 s0, s30, 0xff
.Ltmp2:
	.loc	2 65 17                         ; standard.py:65:17 @[ candidate.py:27:42 ]
	sl_add_i32 s1, s31, 0xff
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
	sl_srl_b32 {s3, wcr}, s3, 0x18
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
	sl_sra_b32 {s0, wcr}, s1, 0x8
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
	sl_mov_b32 s38, 0xffffffff
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
	sl_csel_b32 s2, s38, 0x0, wcr
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
	sl_csel_b32 s2, s38, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_sub_i32 s2, s16, s13
	sl_add_i32 s3, s16, s13
	sl_csel_b32 s2, s16, s2, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s2, s3, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s1, s38, s1, wcr
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
	sl_csel_b32 s2, s38, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_add_i32 s2, s3, 0x1
	sl_add_i32 s4, s3, 0xffffffff
	sl_csel_b32 s2, s3, s2, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s2, s4, wcr
	sl_xor_b32 {s1, wcr}, s1, s11
	sl_sub_i32 s1, s1, s11
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s38, s1, wcr
	.loc	1 32 10 is_stmt 1               ; candidate.py:32:10
	sl_mull_u32 s11, s12, 0x100
	.loc	1 34 44                         ; candidate.py:34:44
	sl_abs_i32 s6, s30
	ml_cvt_f32_u32  v0, s6
	.loc	1 32 25                         ; candidate.py:32:25
	sl_bfe2_b32 s1, tcr_lo, 0x86
	.loc	1 34 44                         ; candidate.py:34:44
	ml_rcp_f32 v0, v0
	.loc	1 33 10                         ; candidate.py:33:10
	sl_mull_u32 s12, s0, 0x100
	.loc	1 34 44                         ; candidate.py:34:44
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_sra_b32 {s7, wcr}, s11, 0x1f
	sl_abs_i32 s4, s11
	sl_or_b32 {s2, wcr}, s0, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s2
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s0
	ml_mov_v2s_b32 s0, v0, 0x0
	sl_mov_b32 s14, 0x0
	ml_mov_b32 v92, 0x0
	ml_mov_b32 v93, 0x0
	sl_mul_u64_u32 s[2:3], s0, s6
	sl_neg_i32 s5, s2
	sl_cmp_eq_u32 wcr, s3, 0x0
	sl_csel_b32 s2, s5, s2, wcr
	sl_mul_u64_u32 s[2:3], s2, s0
	sl_add_i32 s2, s0, s3
	sl_sub_i32 s0, s0, s3
	sl_csel_b32 s0, s2, s0, wcr
	sl_mul_u64_u32 s[2:3], s0, s4
	sl_mull_u32 s0, s3, s6
	sl_sub_i32 s13, s4, s0
	sl_cmp_ge_u32 wcr, s13, s6
	sl_sub_bi_u64 s[2:3], s[8:9], s[8:9], wcr
	sl_cmp_ge_u32 wcr, s4, s0
	sl_sub_bi_u32 s0, s8, s8, wcr
	sl_sub_bi_u64 s[4:5], s[8:9], s[8:9], wcr
	sl_and_b64 {s[2:3], wcr}, s[2:3], s[4:5]
	sl_or_b32 {s2, wcr}, s2, s3
	sl_csel_b32 s2, s38, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_sub_i32 s2, s13, s6
	sl_add_i32 s3, s13, s6
	sl_csel_b32 s2, s13, s2, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s2, s3, wcr
	sl_xor_b32 {s0, wcr}, s0, s7
	sl_sub_i32 s0, s0, s7
	sl_cmp_ne_u32 wcr, s30, 0x0
	sl_csel_b32 s0, s0, 0xffffffff, wcr
	.loc	1 36 21                         ; candidate.py:36:21
	sl_mull_u32 s2, s0, s33
	.loc	1 36 9 is_stmt 0                ; candidate.py:36:9
	sl_sra_b32 {s3, wcr}, s2, 0x1f
	sl_shl_b64 {s[2:3], wcr}, s[2:3], 0x1
	sl_add_i64 s[36:37], s[24:25], s[2:3]
	.loc	1 42 18 is_stmt 1               ; candidate.py:42:18
	sl_mull_u32 s3, s33, 0x2
	sl_mov_b32 s39, s3
	sl_mull_u32 s13, s1, 0x400
	sl_mull_u32 s0, s1, s33
	sl_mull_u32 s4, s0, 0x20
	sl_mov_b32 s5, s13
	sl_sme_load_16x1b64_rowxfb16 s[36:39], s[4:5], 0x0, 0x0, 0x0, 0x1
.Ltmp12:
	.loc	2 65 17                         ; standard.py:65:17 @[ candidate.py:41:35 ]
	sl_add_i32 s0, s32, 0x1f
.Ltmp13:
	.loc	1 41 25                         ; candidate.py:41:25
	sl_cmp_gt_i32 wcr, s0, 0x1f
	ml_mov_b32 v94, 0x0
	ml_mov_b32 v95, 0x0
	ml_mov_b32 v88, 0x0
	ml_mov_b32 v89, 0x0
	ml_mov_b32 v90, 0x0
	ml_mov_b32 v91, 0x0
	ml_mov_b32 v84, 0x0
	ml_mov_b32 v85, 0x0
	ml_mov_b32 v86, 0x0
	ml_mov_b32 v87, 0x0
	ml_mov_b32 v80, 0x0
	ml_mov_b32 v81, 0x0
	ml_mov_b32 v82, 0x0
	ml_mov_b32 v83, 0x0
	ml_mov_b32 v76, 0x0
	ml_mov_b32 v77, 0x0
	ml_mov_b32 v78, 0x0
	ml_mov_b32 v79, 0x0
	ml_mov_b32 v72, 0x0
	ml_mov_b32 v73, 0x0
	ml_mov_b32 v74, 0x0
	ml_mov_b32 v75, 0x0
	ml_mov_b32 v68, 0x0
	ml_mov_b32 v69, 0x0
	ml_mov_b32 v70, 0x0
	ml_mov_b32 v71, 0x0
	ml_mov_b32 v65, 0x0
	ml_mov_b32 v66, 0x0
	ml_mov_b32 v67, 0x0
	ml_mov_b32 v55, 0x0
	ml_mov_b32 v51, 0x0
	ml_mov_b32 v52, 0x0
	ml_mov_b32 v53, 0x0
	ml_mov_b32 v54, 0x0
	ml_mov_b32 v39, 0x0
	ml_mov_b32 v48, 0x0
	ml_mov_b32 v49, 0x0
	ml_mov_b32 v50, 0x0
	ml_mov_b32 v27, 0x0
	ml_mov_b32 v32, 0x0
	ml_mov_b32 v33, 0x0
	ml_mov_b32 v35, 0x0
	ml_mov_b32 v34, 0x0
	ml_mov_b32 v37, 0x0
	ml_mov_b32 v36, 0x0
	ml_mov_b32 v38, 0x0
	ml_mov_b32 v19, 0x0
	ml_mov_b32 v20, 0x0
	ml_mov_b32 v22, 0x0
	ml_mov_b32 v24, 0x0
	ml_mov_b32 v21, 0x0
	ml_mov_b32 v23, 0x0
	ml_mov_b32 v25, 0x0
	ml_mov_b32 v26, 0x0
	ml_mov_b32 v11, 0x0
	ml_mov_b32 v13, 0x0
	ml_mov_b32 v15, 0x0
	ml_mov_b32 v17, 0x0
	ml_mov_b32 v12, 0x0
	ml_mov_b32 v14, 0x0
	ml_mov_b32 v16, 0x0
	ml_mov_b32 v18, 0x0
	sl_cbr_wcrz BB0_4, wcr
; %bb.1:                                ; %.lr.ph
	.loc	1 0 0 is_stmt 0                 ; candidate.py:0
	sl_srl_b32 {s2, wcr}, s10, 0x6
.Ltmp14:
	.loc	2 65 30 is_stmt 1               ; standard.py:65:30 @[ candidate.py:41:35 ]
	sl_sra_b32 {s5, wcr}, s0, 0x1f
	sl_srl_b32 {s5, wcr}, s5, 0x1b
	sl_add_i32 s0, s0, s5
	sl_sra_b32 {s15, wcr}, s0, 0x5
.Ltmp15:
	.loc	1 39 19                         ; candidate.py:39:19
	sl_srl_b32 {s0, wcr}, s12, 0x8
	.loc	1 39 25 is_stmt 0               ; candidate.py:39:25
	sl_mull_u32 s0, s32, s0
	sl_mull_u32 s18, s0, 0x100
	.loc	1 39 9                          ; candidate.py:39:9
	sl_sra_b32 {s19, wcr}, s18, 0x1f
	ml_shl_b32 v0, v64, 0x2
	ml_and_b32 v65, v0, 0xcfc
	sl_srl_b32 {s0, wcr}, s1, 0x1
	sl_mull_u32 s1, s0, 0x40
	sl_mull_u32 s2, s2, 0x2000
	sl_and_b32 {s2, wcr}, s2, 0x2000
	sl_add_i32 s6, s1, s2
	sl_mull_u32 s0, s0, 0x400
	sl_add_i32 s0, s2, s0
	sl_add_i32 s7, s0, 0x8000
	sl_and_b32 {s0, wcr}, s10, 0x40
	sl_mov_b32 s0, 0x280
	sl_csel_b32 s0, s0, 0x0, wcr
	sl_mull_u32 s1, s10, 0x8
	sl_and_b32 {s16, wcr}, s1, 0x400
	ml_mov_b32 v1, 0xfc
	ml_anyop3_b32 v66, s0, v0, v1, 0x6a
	.loc	1 41 25 is_stmt 1               ; candidate.py:41:25
	sl_add_i64 s[0:1], s[36:37], 0x40
	sl_shl_b64 {s[18:19], wcr}, s[18:19], 0x1
	sl_add_i64 s[36:37], s[26:27], s[18:19]
	ml_mov_b32 v0, 0x0
	ml_xor_b32 v67, v65, 0x80
	sl_mov_b32 s39, 0x200
	sl_mov_b32 s17, s38
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v2, 0x0
	ml_mov_b32 v3, 0x0
	ml_mov_b32 v4, 0x0
	ml_mov_b32 v5, 0x0
	ml_mov_b32 v6, 0x0
	ml_mov_b32 v7, 0x0
	ml_mov_b32 v8, 0x0
	ml_mov_b32 v9, 0x0
	ml_mov_b32 v10, 0x0
	ml_mov_b32 v40, 0x0
	ml_mov_b32 v41, 0x0
	ml_mov_b32 v42, 0x0
	ml_mov_b32 v43, 0x0
	ml_mov_b32 v56, 0x0
	ml_mov_b32 v57, 0x0
	ml_mov_b32 v58, 0x0
	ml_mov_b32 v59, 0x0
	ml_mov_b32 v28, 0x0
	ml_mov_b32 v29, 0x0
	ml_mov_b32 v30, 0x0
	ml_mov_b32 v31, 0x0
	ml_mov_b32 v44, 0x0
	ml_mov_b32 v45, 0x0
	ml_mov_b32 v46, 0x0
	ml_mov_b32 v47, 0x0
	ml_mov_b32 v60, 0x0
	ml_mov_b32 v61, 0x0
	ml_mov_b32 v62, 0x0
	ml_mov_b32 v63, 0x0
BB0_2:                                  ; =>This Inner Loop Header: Depth=1
	sl_add_i32 s2, s17, 0x1
	sl_cmp_lt_i32 wcr, s2, 0x2
	sl_csel_b32 s17, s2, 0x0, wcr
	.loc	1 42 18                         ; candidate.py:42:18
	sl_wait g2scnt(0)
	sl_barrier_req 0x0
	sl_barrier_wait 0x0
	.loc	1 42 32 is_stmt 0               ; candidate.py:42:32
	sl_sme_load_16x1b64_rowxfb16 s[36:39], s[6:7], 0x0, 0x0, 0x0, 0x1
	.loc	1 42 18                         ; candidate.py:42:18
	sl_mull_u32 s2, s17, 0x4000
	ml_slb_load_b32x1  v68, v65, s2, #0, null
	sl_add_i32 s5, s2, 0x1000
	sl_add_i32 s18, s2, 0x2000
	sl_add_i32 s19, s2, 0x3000
	ml_slb_load_b32x1  v69, v65, s2, #256, null
	ml_slb_load_b32x1  v70, v65, s5, #0, null
	ml_slb_load_b32x1  v71, v65, s5, #256, null
	ml_slb_load_b32x1  v72, v65, s18, #0, null
	ml_slb_load_b32x1  v73, v65, s18, #256, null
	ml_slb_load_b32x1  v74, v65, s19, #0, null
	ml_slb_load_b32x1  v75, v65, s19, #256, null
	ml_slb_load_b32x1  v76, v67, s2, #512, null
	ml_slb_load_b32x1  v77, v67, s2, #768, null
	ml_slb_load_b32x1  v78, v67, s5, #512, null
	ml_slb_load_b32x1  v79, v67, s5, #768, null
	ml_slb_load_b32x1  v80, v67, s18, #512, null
	ml_slb_load_b32x1  v81, v67, s18, #768, null
	ml_slb_load_b32x1  v82, v67, s19, #512, null
	ml_slb_load_b32x1  v83, v67, s19, #768, null
	.loc	1 42 32                         ; candidate.py:42:32
	sl_wait lmcnt(0) g2scnt(0)
	sl_barrier 
	sl_add_i32 s18, s16, 0x8000
	ml_slb_load_b32x1  v84, v66, s18, #0, null
	sl_add_i32 s19, s16, 0x8800
	sl_add_i32 s20, s16, 0x9000
	sl_add_i32 s21, s16, 0x9800
	ml_slb_load_b32x1  v85, v66, s18, #256, null
	sl_add_i32 s22, s16, 0xa000
	sl_add_i32 s23, s16, 0xa800
	sl_add_i32 s24, s16, 0xb000
	ml_slb_load_b32x1  v86, v66, s19, #0, null
	.loc	1 41 25 is_stmt 1               ; candidate.py:41:25
	sl_add_i32 s2, s14, 0x1
	sl_cmp_lt_i32 wcr, s2, 0x2
	sl_csel_b32 s14, s2, 0x0, wcr
	.loc	1 42 32                         ; candidate.py:42:32
	ml_slb_load_b32x1  v87, v66, s19, #256, null
	.loc	1 42 18 is_stmt 0               ; candidate.py:42:18
	sl_mull_u32 s5, s14, 0x4000
	sl_mov_b32 s2, s38
	sl_add_i32 s5, s13, s5
	.loc	1 42 32                         ; candidate.py:42:32
	ml_slb_load_b32x1  v88, v66, s20, #0, null
	.loc	1 42 18                         ; candidate.py:42:18
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[4:5], 0x0, 0x0, 0x0, 0x1
	.loc	1 42 32                         ; candidate.py:42:32
	sl_add_i32 s2, s16, 0xb800
	.loc	1 41 25 is_stmt 1               ; candidate.py:41:25
	sl_add_i64 s[0:1], s[0:1], 0x40
	.loc	1 42 32                         ; candidate.py:42:32
	ml_slb_load_b32x1  v89, v66, s20, #256, null
	.loc	1 41 25                         ; candidate.py:41:25
	sl_add_i32 s15, s15, 0xffffffff
	sl_cmp_eq_u32 wcr, s15, 0x0
	sl_add_i64 s[36:37], s[36:37], 0x4000
	.loc	1 43 22                         ; candidate.py:43:22
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[68:69], v[84:85], v[0:3]
	.loc	1 42 32                         ; candidate.py:42:32
	ml_slb_load_b32x1  v90, v66, s21, #0, null
	ml_slb_load_b32x1  v91, v66, s21, #256, null
	.loc	1 43 22                         ; candidate.py:43:22
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[68:69], v[86:87], v[4:7]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[68:69], v[88:89], v[8:11]
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[70:71], v[84:85], v[16:19]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[68:69], v[90:91], v[12:15]
	.loc	1 42 32                         ; candidate.py:42:32
	ml_slb_load_b32x1  v68, v66, s22, #0, null
	ml_slb_load_b32x1  v69, v66, s22, #256, null
	.loc	1 43 22                         ; candidate.py:43:22
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[70:71], v[86:87], v[20:23]
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[70:71], v[88:89], v[24:27]
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[70:71], v[90:91], v[28:31]
	.loc	1 42 32                         ; candidate.py:42:32
	ml_slb_load_b32x1  v70, v66, s23, #0, null
	ml_slb_load_b32x1  v71, v66, s23, #256, null
	.loc	1 43 22                         ; candidate.py:43:22
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[72:73], v[84:85], v[32:35]
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[72:73], v[86:87], v[36:39]
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[72:73], v[88:89], v[40:43]
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[72:73], v[90:91], v[44:47]
	.loc	1 42 32                         ; candidate.py:42:32
	ml_slb_load_b32x1  v72, v66, s24, #0, null
	ml_slb_load_b32x1  v73, v66, s24, #256, null
	.loc	1 43 22                         ; candidate.py:43:22
	ml_matrix_mad_f32_bf16_m16n16k16 v[48:51], v[74:75], v[84:85], v[48:51]
	ml_matrix_mad_f32_bf16_m16n16k16 v[52:55], v[74:75], v[86:87], v[52:55]
	ml_matrix_mad_f32_bf16_m16n16k16 v[56:59], v[74:75], v[88:89], v[56:59]
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[74:75], v[90:91], v[60:63]
	.loc	1 42 32                         ; candidate.py:42:32
	ml_slb_load_b32x1  v74, v66, s2, #0, null
	ml_slb_load_b32x1  v75, v66, s2, #256, null
	.loc	1 43 22                         ; candidate.py:43:22
	sl_wait lmcnt(6)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[76:77], v[68:69], v[0:3]
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[76:77], v[70:71], v[4:7]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[76:77], v[72:73], v[8:11]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[76:77], v[74:75], v[12:15]
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[78:79], v[68:69], v[16:19]
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[78:79], v[70:71], v[20:23]
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[78:79], v[72:73], v[24:27]
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[78:79], v[74:75], v[28:31]
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[80:81], v[68:69], v[32:35]
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[80:81], v[70:71], v[36:39]
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[80:81], v[72:73], v[40:43]
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[80:81], v[74:75], v[44:47]
	ml_matrix_mad_f32_bf16_m16n16k16 v[48:51], v[82:83], v[68:69], v[48:51]
	ml_matrix_mad_f32_bf16_m16n16k16 v[52:55], v[82:83], v[70:71], v[52:55]
	ml_matrix_mad_f32_bf16_m16n16k16 v[56:59], v[82:83], v[72:73], v[56:59]
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[82:83], v[74:75], v[60:63]
	.loc	1 41 25                         ; candidate.py:41:25
	sl_cbr_wcrz BB0_2, wcr
; %bb.3:                                ; %._crit_edge.loopexit
	.loc	1 47 48                         ; candidate.py:47:48
	ml_cvt_bf16_f32  v92, v0
	ml_cvt_bf16_f32  v93, v1
	ml_cvt_bf16_f32  v94, v2
	ml_cvt_bf16_f32  v95, v3
	ml_cvt_bf16_f32  v88, v16
	ml_cvt_bf16_f32  v89, v17
	ml_cvt_bf16_f32  v90, v18
	ml_cvt_bf16_f32  v91, v19
	ml_cvt_bf16_f32  v84, v32
	ml_cvt_bf16_f32  v85, v33
	ml_cvt_bf16_f32  v86, v34
	ml_cvt_bf16_f32  v87, v35
	ml_cvt_bf16_f32  v80, v48
	ml_cvt_bf16_f32  v81, v49
	ml_cvt_bf16_f32  v82, v50
	ml_cvt_bf16_f32  v83, v51
	ml_cvt_bf16_f32  v76, v4
	ml_cvt_bf16_f32  v77, v5
	ml_cvt_bf16_f32  v78, v6
	ml_cvt_bf16_f32  v79, v7
	ml_cvt_bf16_f32  v72, v20
	ml_cvt_bf16_f32  v73, v21
	ml_cvt_bf16_f32  v74, v22
	ml_cvt_bf16_f32  v75, v23
	ml_cvt_bf16_f32  v68, v36
	ml_cvt_bf16_f32  v69, v37
	ml_cvt_bf16_f32  v70, v38
	ml_cvt_bf16_f32  v71, v39
	ml_cvt_bf16_f32  v65, v52
	ml_cvt_bf16_f32  v66, v53
	ml_cvt_bf16_f32  v67, v54
	ml_cvt_bf16_f32  v55, v55
	ml_cvt_bf16_f32  v51, v8
	ml_cvt_bf16_f32  v52, v9
	ml_cvt_bf16_f32  v53, v10
	ml_cvt_bf16_f32  v54, v11
	ml_cvt_bf16_f32  v39, v24
	ml_cvt_bf16_f32  v48, v25
	ml_cvt_bf16_f32  v49, v26
	ml_cvt_bf16_f32  v50, v27
	ml_cvt_bf16_f32  v27, v40
	ml_cvt_bf16_f32  v32, v41
	ml_cvt_bf16_f32  v33, v42
	ml_cvt_bf16_f32  v35, v43
	ml_cvt_bf16_f32  v34, v56
	ml_cvt_bf16_f32  v37, v57
	ml_cvt_bf16_f32  v36, v58
	ml_cvt_bf16_f32  v38, v59
	ml_cvt_bf16_f32  v19, v12
	ml_cvt_bf16_f32  v20, v13
	ml_cvt_bf16_f32  v22, v14
	ml_cvt_bf16_f32  v24, v15
	ml_cvt_bf16_f32  v21, v28
	ml_cvt_bf16_f32  v23, v29
	ml_cvt_bf16_f32  v25, v30
	ml_cvt_bf16_f32  v26, v31
	ml_cvt_bf16_f32  v11, v44
	ml_cvt_bf16_f32  v13, v45
	ml_cvt_bf16_f32  v15, v46
	ml_cvt_bf16_f32  v17, v47
	ml_cvt_bf16_f32  v12, v60
	ml_cvt_bf16_f32  v14, v61
	ml_cvt_bf16_f32  v16, v62
	ml_cvt_bf16_f32  v18, v63
BB0_4:                                  ; %._crit_edge
	.loc	1 32 25                         ; candidate.py:32:25
	ml_shl_b32 v42, v64, 0x1
	ml_and_b32 v0, v42, 0xe
	sl_srl_b32 {s0, wcr}, s10, 0x2
	sl_and_b32 {s0, wcr}, s0, 0x30
	.loc	1 33 13                         ; candidate.py:33:13
	sl_add_i32 s0, s12, s0
	ml_add_i32 v29, s0, v0
	ml_add_i32 v28, v29, 0xc0
	ml_add_i32 v30, v29, 0x80
	ml_add_i32 v31, v29, 0x40
	.loc	1 32 25                         ; candidate.py:32:25
	ml_bfe2_b32 v0, v64, 0x63
	sl_srl_b32 {s0, wcr}, s10, 0x4
	sl_and_b32 {s0, wcr}, s0, 0x30
	.loc	1 32 13 is_stmt 0               ; candidate.py:32:13
	sl_add_i32 s0, s11, s0
	ml_add_i32 v2, s0, v0
	ml_add_i32 v43, v2, 0xc8
	ml_add_i32 v44, v2, 0xc0
	ml_add_i32 v45, v2, 0x88
	ml_add_i32 v46, v2, 0x80
	ml_add_i32 v47, v2, 0x48
	ml_add_i32 v56, v2, 0x40
	ml_add_i32 v57, v2, 0x8
	.loc	1 41 25 is_stmt 1               ; candidate.py:41:25
	sl_wait g2scnt(0)
	sl_barrier 
	.loc	1 47 26                         ; candidate.py:47:26
	ml_mul_u64_u32 v[40:41], s34, v2
	.loc	1 47 48 is_stmt 0               ; candidate.py:47:48
	sl_mov_b32 s26, 0x1000504
	sl_mov_b32 s27, 0x2010200
	.loc	1 47 26                         ; candidate.py:47:26
	ml_mul_u64_u32 v[9:10], s34, v57
	ml_mul_u64_u32 v[6:7], s34, v56
	ml_mul_u64_u32 v[7:8], s34, v47
	ml_mul_u64_u32 v[3:4], s34, v46
	ml_mul_u64_u32 v[4:5], s34, v45
	ml_mul_u64_u32 v[0:1], s34, v44
	.loc	1 46 21 is_stmt 1               ; candidate.py:46:21
	ml_cmp_gt_i32 tcr, s30, v2
	.loc	1 47 26                         ; candidate.py:47:26
	ml_mul_u64_u32 v[1:2], s34, v43
	.loc	1 46 21                         ; candidate.py:46:21
	sl_mov_b64 s[2:3], tcr
	ml_cmp_gt_i32 tcr, s30, v57
	.loc	1 47 15                         ; candidate.py:47:15
	ml_sra_b32 v2, v40, 0x1f
	ml_shl_b32 v5, v40, 0x1
	ml_shl_b32 v2, v2, 0x1
	.loc	1 46 21                         ; candidate.py:46:21
	sl_mov_b64 s[0:1], tcr
	ml_cmp_gt_i32 tcr, s30, v56
	.loc	1 47 15                         ; candidate.py:47:15
	ml_srl_b32 v8, v40, 0x1f
	ml_or_b32 v2, v2, v8
	ml_mov_b32 v8, s29
	.loc	1 46 21                         ; candidate.py:46:21
	sl_mov_b64 s[18:19], tcr
	ml_cmp_gt_i32 tcr, s30, v47
	.loc	1 47 30                         ; candidate.py:47:30
	ml_shl_b32 v10, v29, 0x1
	.loc	1 47 48 is_stmt 0               ; candidate.py:47:48
	ml_and_b32 v41, tid, 0x1
	ml_and_b32 v47, tid, 0x20
	.loc	1 46 21 is_stmt 1               ; candidate.py:46:21
	sl_mov_b64 s[16:17], tcr
	ml_cmp_gt_i32 tcr, s30, v46
	.loc	1 47 48                         ; candidate.py:47:48
	ml_bfe2_b32 v46, tid, 0x25
	ml_anyop3_b32 v42, 62, v42, v46, 0xfffffff8
	.loc	1 46 21                         ; candidate.py:46:21
	sl_mov_b64 s[14:15], tcr
	ml_cmp_gt_i32 tcr, s30, v45
	sl_mov_b64 s[10:11], tcr
	ml_cmp_gt_i32 tcr, s30, v44
	sl_mov_b64 s[6:7], tcr
	ml_cmp_gt_i32 tcr, s30, v43
	ml_mov_b32 v43, 0x5410
	sl_mov_b64 s[4:5], tcr
	.loc	1 46 36 is_stmt 0               ; candidate.py:46:36
	ml_cmp_gt_i32 tcr, s31, v29
	sl_mov_b64 s[24:25], tcr
	ml_cmp_gt_i32 tcr, s31, v31
	.loc	1 46 25                         ; candidate.py:46:25
	sl_and_b64 {s[32:33], wcr}, s[2:3], s[24:25]
	.loc	1 46 36                         ; candidate.py:46:36
	sl_mov_b64 s[22:23], tcr
	ml_cmp_gt_i32 tcr, s31, v30
	sl_mov_b64 s[20:21], tcr
	ml_cmp_gt_i32 tcr, s31, v28
	.loc	1 47 61 is_stmt 1               ; candidate.py:47:61
	sl_mov_b32 s31, s38
	.loc	1 46 36                         ; candidate.py:46:36
	sl_mov_b64 s[12:13], tcr
	.loc	1 47 15                         ; candidate.py:47:15
	ml_addo_u32 {v5, tcr}, s28, v5
	ml_addc_i32 v2, v8, v2, tcr
	.loc	1 47 30 is_stmt 0               ; candidate.py:47:30
	ml_sra_b32 v8, v29, 0x1f
	ml_addo_u32 {v5, tcr}, v10, v5
	ml_shl_b32 v8, v8, 0x1
	ml_srl_b32 v10, v29, 0x1f
	ml_or_b32 v8, v8, v10
	ml_addc_i32 v2, v2, v8, tcr
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v8, v93, v92, s26
	ml_byte_permute_b32 v10, v95, v94, s26
	ml_cmp_eq_u32 tcr, v41, 0x0
	ml_mov_b32 v41, 0x7632
	ml_csel_b32 v44, v43, v41, tcr
	ml_byte_permute_b32 v44, v44, v44, s27
	ml_pk_shl_b16 v44, v44, 0x40004
	ml_pk_srl_b8 v44, v44, 0x40004
	ml_byte_permute_b32 v45, v8, v10, v44
	ml_slb_shuffle_rtn_b32 v45, v45, v42
	ml_csel_b32 v46, v41, v43, tcr
	ml_byte_permute_b32 v46, v46, v46, s27
	ml_pk_shl_b16 v46, v46, 0x40004
	ml_pk_srl_b8 v46, v46, 0x40004
	ml_byte_permute_b32 v8, v8, v10, v46
	ml_xor_b32 v10, v42, 0x1
	ml_slb_shuffle_rtn_b32 v8, v8, v10
	ml_cmp_eq_u32 tcr, v47, 0x0
	ml_mov_b32 v47, 0x1054
	ml_csel_b32 v43, v43, v47, tcr
	ml_byte_permute_b32 v43, v43, v43, s27
	.loc	1 47 61                         ; candidate.py:47:61
	ml_mov_v2s_b32 s28, v5, 0x0
	.loc	1 47 48                         ; candidate.py:47:48
	ml_pk_shl_b16 v43, v43, 0x40004
	ml_pk_srl_b8 v43, v43, 0x40004
	.loc	1 47 61                         ; candidate.py:47:61
	ml_mov_v2s_b32 s29, v2, 0x0
	ml_mov_b32 v2, s28
	ml_sub_i32 v2, v5, v2
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v5, v45, v8, v43
	.loc	1 47 61                         ; candidate.py:47:61
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[32:33], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v2, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v89, v88, s26
	ml_byte_permute_b32 v47, v91, v90, s26
	ml_byte_permute_b32 v56, v5, v47, v44
	ml_slb_shuffle_rtn_b32 v56, v56, v42
	ml_byte_permute_b32 v5, v5, v47, v46
	ml_mov_b32 v47, 0x3276
	ml_csel_b32 v41, v41, v47, tcr
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[32:33], wcr}, s[24:25], s[0:1]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_slb_shuffle_rtn_b32 v5, v5, v10
	ml_byte_permute_b32 v41, v41, v41, s27
	ml_pk_shl_b16 v41, v41, 0x40004
	ml_pk_srl_b8 v41, v41, 0x40004
	ml_byte_permute_b32 v8, v45, v8, v41
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_sub_i32 v45, v9, v40
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s27, v45, 0x0
	ml_sub_i32 v45, v6, v40
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s30, v45, 0x0
	ml_add_i32 v45, s27, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[32:33], tmsk
	ml_lsa_store_dword v8, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[32:33], wcr}, s[24:25], s[18:19]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v8, v56, v5, v43
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v45, s30, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[32:33], tmsk
	ml_lsa_store_dword v8, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v8, v85, v84, s26
	ml_byte_permute_b32 v45, v87, v86, s26
	ml_byte_permute_b32 v47, v8, v45, v44
	ml_slb_shuffle_rtn_b32 v47, v47, v42
	ml_byte_permute_b32 v8, v8, v45, v46
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[32:33], wcr}, s[24:25], s[16:17]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v56, v5, v41
	ml_slb_shuffle_rtn_b32 v8, v8, v10
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_sub_i32 v45, v7, v40
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s27, v45, 0x0
	ml_sub_i32 v45, v3, v40
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s30, v45, 0x0
	ml_add_i32 v45, s27, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[32:33], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[32:33], wcr}, s[24:25], s[14:15]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v5, v47, v8, v43
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v45, s30, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[32:33], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v81, v80, s26
	ml_byte_permute_b32 v45, v83, v82, s26
	ml_byte_permute_b32 v56, v5, v45, v44
	ml_slb_shuffle_rtn_b32 v56, v56, v42
	ml_byte_permute_b32 v5, v5, v45, v46
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[32:33], wcr}, s[24:25], s[10:11]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v8, v47, v8, v41
	ml_slb_shuffle_rtn_b32 v5, v5, v10
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_sub_i32 v45, v4, v40
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s27, v45, 0x0
	ml_sub_i32 v45, v0, v40
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s30, v45, 0x0
	ml_add_i32 v45, s27, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[32:33], tmsk
	ml_lsa_store_dword v8, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[32:33], wcr}, s[24:25], s[6:7]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v8, v56, v5, v43
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v45, s30, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[32:33], tmsk
	ml_lsa_store_dword v8, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v8, v77, v76, s26
	ml_byte_permute_b32 v45, v79, v78, s26
	ml_byte_permute_b32 v47, v8, v45, v44
	ml_slb_shuffle_rtn_b32 v47, v47, v42
	ml_byte_permute_b32 v8, v8, v45, v46
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[24:25], wcr}, s[24:25], s[4:5]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v56, v5, v41
	ml_slb_shuffle_rtn_b32 v8, v8, v10
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_sub_i32 v45, v1, v40
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s27, v45, 0x0
	ml_sub_i32 v45, v31, v29
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s30, v45, 0x0
	ml_add_i32 v45, s27, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[24:25], wcr}, s[2:3], s[22:23]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v5, v47, v8, v43
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v45, s30, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v73, v72, s26
	ml_byte_permute_b32 v45, v75, v74, s26
	ml_byte_permute_b32 v56, v5, v45, v44
	ml_slb_shuffle_rtn_b32 v56, v56, v42
	.loc	1 47 30                         ; candidate.py:47:30
	ml_add_i32 v40, v29, v40
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v5, v45, v46
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[24:25], wcr}, s[0:1], s[22:23]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_slb_shuffle_rtn_b32 v5, v5, v10
	ml_byte_permute_b32 v8, v47, v8, v41
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v45, v31, v9
	ml_sub_i32 v45, v45, v40
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s27, v45, 0x0
	ml_add_i32 v45, v31, v6
	ml_sub_i32 v45, v45, v40
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s30, v45, 0x0
	ml_add_i32 v45, s27, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v8, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[24:25], wcr}, s[18:19], s[22:23]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v8, v56, v5, v43
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v45, s30, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v8, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v8, v69, v68, s26
	ml_byte_permute_b32 v45, v71, v70, s26
	ml_byte_permute_b32 v47, v8, v45, v44
	ml_slb_shuffle_rtn_b32 v47, v47, v42
	ml_byte_permute_b32 v8, v8, v45, v46
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[24:25], wcr}, s[16:17], s[22:23]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v56, v5, v41
	ml_slb_shuffle_rtn_b32 v8, v8, v10
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v45, v31, v7
	ml_sub_i32 v45, v45, v40
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s27, v45, 0x0
	ml_add_i32 v45, v31, v3
	ml_sub_i32 v45, v45, v40
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s30, v45, 0x0
	ml_add_i32 v45, s27, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[24:25], wcr}, s[14:15], s[22:23]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v5, v47, v8, v43
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v45, s30, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v66, v65, s26
	ml_byte_permute_b32 v45, v55, v67, s26
	ml_byte_permute_b32 v55, v5, v45, v44
	ml_slb_shuffle_rtn_b32 v55, v55, v42
	ml_byte_permute_b32 v5, v5, v45, v46
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[24:25], wcr}, s[10:11], s[22:23]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v8, v47, v8, v41
	ml_slb_shuffle_rtn_b32 v5, v5, v10
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v45, v31, v4
	ml_sub_i32 v45, v45, v40
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s27, v45, 0x0
	ml_add_i32 v45, v31, v0
	ml_sub_i32 v45, v45, v40
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s30, v45, 0x0
	ml_add_i32 v45, s27, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v8, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[24:25], wcr}, s[6:7], s[22:23]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v8, v55, v5, v43
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v45, s30, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v8, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v8, v52, v51, s26
	ml_byte_permute_b32 v45, v54, v53, s26
	ml_byte_permute_b32 v47, v8, v45, v44
	ml_slb_shuffle_rtn_b32 v47, v47, v42
	ml_byte_permute_b32 v8, v8, v45, v46
	ml_byte_permute_b32 v5, v55, v5, v41
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[22:23], wcr}, s[4:5], s[22:23]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_slb_shuffle_rtn_b32 v8, v8, v10
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v31, v31, v1
	ml_sub_i32 v31, v31, v40
	ml_shl_b32 v31, v31, 0x1
	ml_mov_v2s_b32 s24, v31, 0x0
	ml_sub_i32 v31, v30, v29
	ml_shl_b32 v31, v31, 0x1
	ml_mov_v2s_b32 s25, v31, 0x0
	ml_add_i32 v31, s24, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v31, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[22:23], wcr}, s[2:3], s[20:21]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v5, v47, v8, v43
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v31, s25, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v31, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v48, v39, s26
	ml_byte_permute_b32 v31, v50, v49, s26
	ml_byte_permute_b32 v39, v5, v31, v44
	ml_slb_shuffle_rtn_b32 v39, v39, v42
	ml_byte_permute_b32 v5, v5, v31, v46
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[22:23], wcr}, s[0:1], s[20:21]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v8, v47, v8, v41
	ml_slb_shuffle_rtn_b32 v5, v5, v10
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v31, v30, v9
	ml_sub_i32 v31, v31, v40
	ml_shl_b32 v31, v31, 0x1
	ml_mov_v2s_b32 s24, v31, 0x0
	ml_add_i32 v31, v30, v6
	ml_sub_i32 v31, v31, v40
	ml_shl_b32 v31, v31, 0x1
	ml_mov_v2s_b32 s25, v31, 0x0
	ml_add_i32 v31, s24, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v8, s[28:31], signed v31, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[22:23], wcr}, s[18:19], s[20:21]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v8, v39, v5, v43
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v31, s25, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v8, s[28:31], signed v31, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v8, v32, v27, s26
	ml_byte_permute_b32 v27, v35, v33, s26
	ml_byte_permute_b32 v31, v8, v27, v44
	ml_slb_shuffle_rtn_b32 v31, v31, v42
	ml_byte_permute_b32 v32, v37, v34, s26
	ml_byte_permute_b32 v8, v8, v27, v46
	ml_byte_permute_b32 v27, v38, v36, s26
	ml_slb_shuffle_rtn_b32 v8, v8, v10
	ml_byte_permute_b32 v33, v32, v27, v44
	ml_byte_permute_b32 v27, v32, v27, v46
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[22:23], wcr}, s[16:17], s[20:21]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_slb_shuffle_rtn_b32 v32, v33, v42
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v33, v30, v7
	ml_sub_i32 v33, v33, v40
	ml_shl_b32 v33, v33, 0x1
	ml_mov_v2s_b32 s27, v33, 0x0
	.loc	1 47 48                         ; candidate.py:47:48
	ml_slb_shuffle_rtn_b32 v27, v27, v10
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[24:25], wcr}, s[14:15], s[20:21]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v39, v5, v41
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v33, s27, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v33, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v5, v31, v8, v43
	.loc	1 47 61                         ; candidate.py:47:61
	ml_add_i32 v33, v30, v3
	ml_sub_i32 v33, v33, v40
	ml_shl_b32 v33, v33, 0x1
	ml_mov_v2s_b32 s22, v33, 0x0
	ml_add_i32 v33, v30, v4
	ml_sub_i32 v33, v33, v40
	ml_shl_b32 v33, v33, 0x1
	ml_mov_v2s_b32 s27, v33, 0x0
	ml_add_i32 v33, s22, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v33, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[22:23], wcr}, s[10:11], s[20:21]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v31, v8, v41
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v8, s27, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v8, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[22:23], wcr}, s[6:7], s[20:21]
	.loc	1 47 61                         ; candidate.py:47:61
	ml_add_i32 v5, v30, v0
	ml_sub_i32 v5, v5, v40
	ml_shl_b32 v5, v5, 0x1
	ml_mov_v2s_b32 s24, v5, 0x0
	.loc	1 47 48 is_stmt 0               ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v5, v32, v27, v43
	.loc	1 47 61                         ; candidate.py:47:61
	ml_add_i32 v8, v30, v1
	ml_sub_i32 v8, v8, v40
	ml_shl_b32 v8, v8, 0x1
	ml_mov_v2s_b32 s25, v8, 0x0
	ml_add_i32 v8, s24, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v8, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[20:21], wcr}, s[4:5], s[20:21]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v32, v27, v41
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v8, s25, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[20:21], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v8, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v20, v19, s26
	ml_byte_permute_b32 v8, v24, v22, s26
	ml_byte_permute_b32 v19, v5, v8, v44
	ml_slb_shuffle_rtn_b32 v19, v19, v42
	ml_byte_permute_b32 v5, v5, v8, v46
	ml_byte_permute_b32 v8, v23, v21, s26
	ml_byte_permute_b32 v20, v26, v25, s26
	ml_slb_shuffle_rtn_b32 v5, v5, v10
	ml_byte_permute_b32 v21, v8, v20, v44
	.loc	1 47 30                         ; candidate.py:47:30
	ml_add_i32 v9, v28, v9
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v8, v8, v20, v46
	ml_slb_shuffle_rtn_b32 v21, v21, v42
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[2:3], wcr}, s[2:3], s[12:13]
	.loc	1 47 61                         ; candidate.py:47:61
	ml_sub_i32 v20, v28, v29
	ml_shl_b32 v20, v20, 0x1
	.loc	1 47 48 is_stmt 0               ; candidate.py:47:48
	ml_slb_shuffle_rtn_b32 v8, v8, v10
	.loc	1 47 61                         ; candidate.py:47:61
	ml_mov_v2s_b32 s20, v20, 0x0
	ml_sub_i32 v9, v9, v40
	ml_shl_b32 v9, v9, 0x1
	ml_mov_v2s_b32 s21, v9, 0x0
	ml_add_i32 v9, s20, v2
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v20, v19, v5, v43
	.loc	1 47 61                         ; candidate.py:47:61
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[2:3], tmsk
	ml_lsa_store_dword v20, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[0:1], wcr}, s[0:1], s[12:13]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v19, v5, v41
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v9, s21, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 30                         ; candidate.py:47:30
	ml_add_i32 v5, v28, v6
	ml_add_i32 v6, v28, v7
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[0:1], wcr}, s[18:19], s[12:13]
	.loc	1 47 61                         ; candidate.py:47:61
	ml_sub_i32 v5, v5, v40
	ml_shl_b32 v5, v5, 0x1
	ml_mov_v2s_b32 s2, v5, 0x0
	.loc	1 47 48 is_stmt 0               ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v5, v21, v8, v43
	.loc	1 47 61                         ; candidate.py:47:61
	ml_sub_i32 v6, v6, v40
	ml_shl_b32 v6, v6, 0x1
	ml_mov_v2s_b32 s3, v6, 0x0
	ml_add_i32 v6, s2, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v6, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[0:1], wcr}, s[16:17], s[12:13]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v21, v8, v41
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v6, s3, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v6, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v13, v11, s26
	ml_byte_permute_b32 v6, v17, v15, s26
	ml_byte_permute_b32 v7, v5, v6, v44
	ml_slb_shuffle_rtn_b32 v7, v7, v42
	.loc	1 47 30                         ; candidate.py:47:30
	ml_add_i32 v3, v28, v3
	ml_add_i32 v4, v28, v4
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v5, v5, v6, v46
	ml_slb_shuffle_rtn_b32 v5, v5, v10
	ml_byte_permute_b32 v6, v14, v12, s26
	ml_byte_permute_b32 v8, v18, v16, s26
	ml_byte_permute_b32 v9, v6, v8, v44
	ml_slb_shuffle_rtn_b32 v9, v9, v42
	.loc	1 47 30                         ; candidate.py:47:30
	ml_add_i32 v0, v28, v0
	ml_add_i32 v1, v28, v1
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v6, v6, v8, v46
	ml_slb_shuffle_rtn_b32 v6, v6, v10
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[0:1], wcr}, s[14:15], s[12:13]
	.loc	1 47 61                         ; candidate.py:47:61
	ml_sub_i32 v3, v3, v40
	ml_shl_b32 v3, v3, 0x1
	ml_mov_v2s_b32 s2, v3, 0x0
	ml_sub_i32 v4, v4, v40
	ml_shl_b32 v4, v4, 0x1
	ml_mov_v2s_b32 s3, v4, 0x0
	ml_add_i32 v4, s2, v2
	.loc	1 47 48 is_stmt 0               ; candidate.py:47:48
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v3, v7, v5, v43
	.loc	1 47 61                         ; candidate.py:47:61
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v3, s[28:31], signed v4, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[0:1], wcr}, s[10:11], s[12:13]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v3, v7, v5, v41
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_add_i32 v4, s3, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v3, s[28:31], signed v4, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	ml_sub_i32 v0, v0, v40
	ml_shl_b32 v0, v0, 0x1
	ml_mov_v2s_b32 s2, v0, 0x0
	ml_sub_i32 v0, v1, v40
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[0:1], wcr}, s[6:7], s[12:13]
	.loc	1 47 48                         ; candidate.py:47:48
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v1, v9, v6, v43
	.loc	1 47 61 is_stmt 0               ; candidate.py:47:61
	ml_shl_b32 v0, v0, 0x1
	ml_mov_v2s_b32 s3, v0, 0x0
	ml_add_i32 v0, s2, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v1, s[28:31], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 48                         ; candidate.py:47:48
	ml_byte_permute_b32 v0, v9, v6, v41
	.loc	1 46 25 is_stmt 1               ; candidate.py:46:25
	sl_and_b64 {s[0:1], wcr}, s[4:5], s[12:13]
	.loc	1 47 61                         ; candidate.py:47:61
	ml_add_i32 v1, s3, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v0, s[28:31], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 47 4 is_stmt 0                ; candidate.py:47:4
	sl_eop 
.Ltmp16:
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	n256_linear.kd
	.type	n256_linear.kd,@object
	.size	n256_linear.kd, 64
n256_linear.kd:
	.asciz	"\000\000\000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	n256_linear@rel64-n256_linear.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	536919
	.asciz	"\003\000\224\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	n256_linear, .Lfunc_end0-n256_linear
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 8032
; NumSgprs: 44
; NumVgprs: 96
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 5
; VGPRBlocks: 23
; NumSGPRsForWarpsPerNU: 40
; NumVGPRsForWarpsPerNR: 96
; ReqNTIDx: 0
; MaxNTIDx: 0
; MinCTASm: 0
; ActiveWarp: 2
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
	.long	230                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0xdf DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"candidate.py"                  ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/workspace/experiments/minicpm-s2/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/source" ; DW_AT_comp_dir
	.byte	0
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.byte	2                               ; Abbrev [2] 0xa1:0xe DW_TAG_subprogram
	.ascii	"n256_linear"                   ; DW_AT_name
	.byte	0
	.byte	1                               ; DW_AT_inline
	.byte	3                               ; Abbrev [3] 0xaf:0x3a DW_TAG_subprogram
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.long	161                             ; DW_AT_abstract_origin
	.byte	4                               ; Abbrev [4] 0xc4:0xc DW_TAG_inlined_subroutine
	.long	161                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges0                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	27                              ; DW_AT_call_line
	.byte	42                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0xd0:0xc DW_TAG_inlined_subroutine
	.long	161                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges1                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	27                              ; DW_AT_call_line
	.byte	21                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0xdc:0xc DW_TAG_inlined_subroutine
	.long	161                             ; DW_AT_abstract_origin
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
    .name:           n256_linear
    .private_segment_fixed_size: 0
    .sgpr_count:     44
    .sgpr_spill_count: 0
    .symbol:         n256_linear.kd
    .vgpr_count:     96
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
