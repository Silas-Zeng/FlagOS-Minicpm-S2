	.text
	.globl	mm_kernel                       ; -- Begin function mm_kernel
	.p2align	3
	.type	mm_kernel,@function
	.iluvatar_kernel mm_kernel
mm_kernel:                              ; @mm_kernel
.Lfunc_begin0:
	.file	1 "/workspace/experiments/minicpm-s2/framework/20261021T173921Z-mm-cta-group-gate/source" "mm_baseline.py"
	.loc	1 21 0                          ; mm_baseline.py:21:0
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
		granulated_workitem_vgpr_count = 24
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
		warp_sgpr_count = 40
		workitem_vgpr_count = 97
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
	ml_vrf_init_u32 v64, tcr
.Ltmp0:
	.file	2 "/usr/local/lib/python3.12/site-packages/triton/language" "standard.py"
	.loc	2 65 17 prologue_end            ; standard.py:65:17 @[ mm_baseline.py:57:24 ]
	sl_lsa_load_b32x16 s[20:35], s[4:5], noreg, #0, ca
.Ltmp1:
	.loc	1 64 19                         ; mm_baseline.py:64:19
	sl_reg_read s2, hwreg(HW_REG_MODE)
.Ltmp2:
	.loc	2 65 17                         ; standard.py:65:17 @[ mm_baseline.py:57:24 ]
	sl_wait smcnt(0)
	sl_add_i32 s0, s27, 0xff
	.loc	2 65 30 is_stmt 0               ; standard.py:65:30 @[ mm_baseline.py:57:24 ]
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_srl_b32 {s1, wcr}, s1, 0x18
	sl_add_i32 s0, s0, s1
.Ltmp3:
	.loc	1 64 19 is_stmt 1               ; mm_baseline.py:64:19
	sl_sra_b32 {s9, wcr}, s0, 0x1f
	sl_sra_b32 {s14, wcr}, s0, 0x8
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_abs_i32 s1, s14
	ml_cvt_f32_u32  v0, s1
	sl_or_b32 {s3, wcr}, s2, 0x3
	ml_rcp_f32 v0, v0
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s3
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s2
	ml_mov_v2s_b32 s4, v0, 0x0
	sl_mov_b32 s34, 0xffffffff
	.loc	1 71 44                         ; mm_baseline.py:71:44
	sl_bfe2_b32 s15, tcr_lo, 0x86
	.loc	1 64 19                         ; mm_baseline.py:64:19
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
	sl_sub_bi_u64 s[12:13], s[10:11], s[10:11], wcr
	sl_and_b64 {s[4:5], wcr}, s[4:5], s[12:13]
	sl_or_b32 {s4, wcr}, s4, s5
	sl_csel_b32 s2, s34, 0x0, wcr
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
	.loc	1 65 18                         ; mm_baseline.py:65:18
	sl_mull_u32 s1, s0, s14
	sl_sub_i32 s6, s6, s1
	.loc	1 71 21                         ; mm_baseline.py:71:21
	sl_mull_u32 s9, s0, 0x100
	.loc	1 72 52                         ; mm_baseline.py:72:52
	sl_abs_i32 s13, s26
	ml_cvt_f32_u32  v0, s13
	.loc	1 71 44                         ; mm_baseline.py:71:44
	sl_and_b32 {s12, wcr}, tcr_lo, 0xc0
	.loc	1 72 52                         ; mm_baseline.py:72:52
	ml_rcp_f32 v0, v0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_sra_b32 {s14, wcr}, s9, 0x1f
	sl_abs_i32 s4, s9
	sl_or_b32 {s1, wcr}, s0, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s0
	ml_mov_v2s_b32 s2, v0, 0x0
	.loc	1 78 52                         ; mm_baseline.py:78:52
	sl_abs_i32 s16, s27
	ml_cvt_f32_u32  v0, s16
	.loc	1 72 52                         ; mm_baseline.py:72:52
	sl_mul_u64_u32 s[0:1], s2, s13
	sl_neg_i32 s3, s0
	sl_cmp_eq_u32 wcr, s1, 0x0
	sl_csel_b32 s0, s3, s0, wcr
	sl_mul_u64_u32 s[0:1], s0, s2
	sl_add_i32 s0, s2, s1
	sl_sub_i32 s1, s2, s1
	sl_csel_b32 s0, s0, s1, wcr
	sl_mul_u64_u32 s[0:1], s0, s4
	sl_mull_u32 s0, s1, s13
	sl_sub_i32 s1, s4, s0
	sl_cmp_ge_u32 wcr, s1, s13
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	sl_cmp_ge_u32 wcr, s4, s0
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_sub_bi_u64 s[4:5], s[10:11], s[10:11], wcr
	sl_and_b64 {s[2:3], wcr}, s[2:3], s[4:5]
	sl_or_b32 {s2, wcr}, s2, s3
	sl_csel_b32 s2, s34, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_sub_i32 s2, s1, s13
	sl_add_i32 s3, s1, s13
	sl_csel_b32 s1, s1, s2, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s1, s3, wcr
	sl_xor_b32 {s0, wcr}, s0, s14
	sl_sub_i32 s0, s0, s14
	.loc	1 78 52                         ; mm_baseline.py:78:52
	ml_rcp_f32 v0, v0
	.loc	1 72 52                         ; mm_baseline.py:72:52
	sl_cmp_ne_u32 wcr, s26, 0x0
	.loc	1 78 52                         ; mm_baseline.py:78:52
	sl_reg_read s1, hwreg(HW_REG_MODE)
	.loc	1 72 52                         ; mm_baseline.py:72:52
	sl_csel_b32 s14, s0, 0xffffffff, wcr
	.loc	1 77 21                         ; mm_baseline.py:77:21
	sl_mull_u32 s13, s6, 0x100
	.loc	1 78 52                         ; mm_baseline.py:78:52
	sl_or_b32 {s0, wcr}, s1, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s0
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_mov_v2s_b32 s2, v0, 0x0
	.loc	1 86 24                         ; mm_baseline.py:86:24
	sl_mull_u32 s35, s29, 0x2
	sl_mull_u32 s6, s15, 0x20
	.loc	1 83 19                         ; mm_baseline.py:83:19
	ml_mov_b32 v93, 0x0
	.loc	1 78 52                         ; mm_baseline.py:78:52
	sl_mul_u64_u32 s[0:1], s2, s16
	sl_neg_i32 s3, s0
	sl_cmp_eq_u32 wcr, s1, 0x0
	sl_csel_b32 s0, s3, s0, wcr
	sl_mul_u64_u32 s[0:1], s0, s2
	sl_add_i32 s0, s2, s1
	sl_sub_i32 s1, s2, s1
	sl_csel_b32 s0, s0, s1, wcr
	sl_mul_u64_u32 s[0:1], s0, s13
	sl_mull_u32 s0, s1, s16
	sl_sub_i32 s1, s13, s0
	sl_cmp_ge_u32 wcr, s1, s16
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	sl_cmp_ge_u32 wcr, s13, s0
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_sub_bi_u64 s[4:5], s[10:11], s[10:11], wcr
	sl_and_b64 {s[2:3], wcr}, s[2:3], s[4:5]
	sl_or_b32 {s2, wcr}, s2, s3
	sl_csel_b32 s2, s34, 0x0, wcr
	sl_cmp_eq_u32 wcr, s2, 0x0
	sl_sub_i32 s2, s1, s16
	sl_add_i32 s3, s1, s16
	sl_csel_b32 s1, s1, s2, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s1, s3, wcr
	sl_cmp_ne_u32 wcr, s27, 0x0
	sl_csel_b32 s2, s0, 0xffffffff, wcr
	.loc	1 79 17                         ; mm_baseline.py:79:17
	sl_mull_u32 s3, s7, 0x20
	.loc	1 81 28                         ; mm_baseline.py:81:28
	sl_mull_u32 s0, s14, s29
	.loc	1 81 40 is_stmt 0               ; mm_baseline.py:81:40
	sl_add_i32 s0, s0, s3
	.loc	1 81 13                         ; mm_baseline.py:81:13
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[32:33], s[20:21], s[0:1]
	.loc	1 86 24 is_stmt 1               ; mm_baseline.py:86:24
	sl_mull_u32 s14, s15, 0x400
	sl_mull_u32 s4, s29, s6
	sl_mov_b32 s5, s14
	sl_sme_load_16x1b64_rowxfb16 s[32:35], s[4:5], 0x0, 0x0, 0x0, 0x1
	.loc	1 82 54                         ; mm_baseline.py:82:54
	sl_mull_u32 s0, s2, s30
	.loc	1 82 39 is_stmt 0               ; mm_baseline.py:82:39
	sl_add_i32 s0, s0, s3
	.loc	1 82 13                         ; mm_baseline.py:82:13
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[0:1], s[22:23], s[0:1]
	.loc	1 87 24 is_stmt 1               ; mm_baseline.py:87:24
	sl_mull_u32 s3, s30, 0x2
	sl_mov_b32 s2, s34
	sl_add_i32 s7, s14, 0x8000
	sl_mull_u32 s6, s30, s6
	sl_sme_load_16x1b64_col s[0:3], s[6:7], 0x0, 0x0, 0x0, 0x1
.Ltmp4:
	.loc	2 65 17                         ; standard.py:65:17 @[ mm_baseline.py:85:37 ]
	sl_add_i32 s2, s28, 0x1f
.Ltmp5:
	.loc	1 85 26                         ; mm_baseline.py:85:26
	sl_cmp_gt_i32 wcr, s2, 0x1f
	sl_mov_b32 s15, 0x0
	ml_mov_b32 v94, 0x0
	ml_mov_b32 v95, 0x0
	ml_mov_b32 v96, 0x0
	ml_mov_b32 v89, 0x0
	ml_mov_b32 v90, 0x0
	ml_mov_b32 v91, 0x0
	ml_mov_b32 v92, 0x0
	ml_mov_b32 v81, 0x0
	ml_mov_b32 v82, 0x0
	ml_mov_b32 v83, 0x0
	ml_mov_b32 v86, 0x0
	ml_mov_b32 v84, 0x0
	ml_mov_b32 v87, 0x0
	ml_mov_b32 v85, 0x0
	ml_mov_b32 v88, 0x0
	ml_mov_b32 v73, 0x0
	ml_mov_b32 v74, 0x0
	ml_mov_b32 v75, 0x0
	ml_mov_b32 v78, 0x0
	ml_mov_b32 v76, 0x0
	ml_mov_b32 v79, 0x0
	ml_mov_b32 v77, 0x0
	ml_mov_b32 v80, 0x0
	ml_mov_b32 v65, 0x0
	ml_mov_b32 v66, 0x0
	ml_mov_b32 v67, 0x0
	ml_mov_b32 v70, 0x0
	ml_mov_b32 v68, 0x0
	ml_mov_b32 v71, 0x0
	ml_mov_b32 v69, 0x0
	ml_mov_b32 v72, 0x0
	ml_mov_b32 v48, 0x0
	ml_mov_b32 v49, 0x0
	ml_mov_b32 v50, 0x0
	ml_mov_b32 v53, 0x0
	ml_mov_b32 v51, 0x0
	ml_mov_b32 v54, 0x0
	ml_mov_b32 v52, 0x0
	ml_mov_b32 v55, 0x0
	ml_mov_b32 v32, 0x0
	ml_mov_b32 v33, 0x0
	ml_mov_b32 v34, 0x0
	ml_mov_b32 v37, 0x0
	ml_mov_b32 v35, 0x0
	ml_mov_b32 v38, 0x0
	ml_mov_b32 v36, 0x0
	ml_mov_b32 v39, 0x0
	ml_mov_b32 v21, 0x0
	ml_mov_b32 v23, 0x0
	ml_mov_b32 v24, 0x0
	ml_mov_b32 v27, 0x0
	ml_mov_b32 v22, 0x0
	ml_mov_b32 v25, 0x0
	ml_mov_b32 v26, 0x0
	ml_mov_b32 v28, 0x0
	ml_mov_b32 v13, 0x0
	ml_mov_b32 v15, 0x0
	ml_mov_b32 v17, 0x0
	ml_mov_b32 v19, 0x0
	ml_mov_b32 v14, 0x0
	ml_mov_b32 v16, 0x0
	ml_mov_b32 v18, 0x0
	ml_mov_b32 v20, 0x0
	sl_cbr_wcrz BB0_4, wcr
; %bb.1:                                ; %.lr.ph
.Ltmp6:
	.loc	2 65 30                         ; standard.py:65:30 @[ mm_baseline.py:85:37 ]
	sl_sra_b32 {s5, wcr}, s2, 0x1f
	sl_srl_b32 {s5, wcr}, s5, 0x1b
	sl_add_i32 s2, s2, s5
	sl_sra_b32 {s16, wcr}, s2, 0x5
	ml_shl_b32 v0, v64, 0x2
	ml_and_b32 v65, v0, 0xcfc
	ml_shl_b32 v1, v64, 0x6
	ml_and_b32 v1, v1, 0x300
	sl_mull_u32 s2, s12, 0x10
	ml_and_b32 v0, v0, 0xfc
	ml_anyop3_b32 v66, s2, v1, v0, 0xfffffffe
	ml_xor_b32 v67, v66, 0x10
	ml_xor_b32 v68, v66, 0x20
	ml_xor_b32 v69, v66, 0x30
.Ltmp7:
	.loc	1 85 26                         ; mm_baseline.py:85:26
	sl_add_i64 s[0:1], s[0:1], 0x40
	sl_add_i64 s[32:33], s[32:33], 0x40
	ml_mov_b32 v0, 0x0
	ml_xor_b32 v70, v65, 0x80
	sl_mov_b32 s17, s34
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
	ml_mov_b32 v11, 0x0
	ml_mov_b32 v40, 0x0
	ml_mov_b32 v41, 0x0
	ml_mov_b32 v42, 0x0
	ml_mov_b32 v43, 0x0
	ml_mov_b32 v56, 0x0
	ml_mov_b32 v57, 0x0
	ml_mov_b32 v58, 0x0
	ml_mov_b32 v59, 0x0
	ml_mov_b32 v12, 0x0
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
	.loc	1 86 24                         ; mm_baseline.py:86:24
	sl_wait g2scnt(0)
	sl_barrier_req 0x0
	sl_barrier_wait 0x0
	sl_mull_u32 s18, s17, 0x4000
	ml_slb_load_b32x1  v71, v65, s18, #0, null
	.loc	1 87 24                         ; mm_baseline.py:87:24
	sl_add_i32 s19, s18, 0x8000
	sl_add_i32 s20, s18, 0x9000
	sl_add_i32 s21, s18, 0xa000
	.loc	1 86 24                         ; mm_baseline.py:86:24
	ml_slb_load_b32x1  v72, v65, s18, #256, null
	.loc	1 87 24                         ; mm_baseline.py:87:24
	sl_add_i32 s22, s18, 0xb000
	.loc	1 86 24                         ; mm_baseline.py:86:24
	sl_add_i32 s23, s18, 0x1000
	sl_add_i32 s28, s18, 0x2000
	.loc	1 87 24                         ; mm_baseline.py:87:24
	ml_slb_load_b32x1  v73, v66, s19, #0, null
	.loc	1 86 24                         ; mm_baseline.py:86:24
	sl_add_i32 s29, s18, 0x3000
	.loc	1 85 26                         ; mm_baseline.py:85:26
	sl_add_i32 s2, s15, 0x1
	sl_cmp_lt_i32 wcr, s2, 0x2
	.loc	1 87 24                         ; mm_baseline.py:87:24
	ml_slb_load_b32x1  v74, v67, s19, #0, null
	.loc	1 85 26                         ; mm_baseline.py:85:26
	sl_csel_b32 s15, s2, 0x0, wcr
	.loc	1 86 24                         ; mm_baseline.py:86:24
	sl_mull_u32 s2, s15, 0x4000
	sl_add_i32 s5, s14, s2
	.loc	1 87 24                         ; mm_baseline.py:87:24
	ml_slb_load_b32x1  v75, v66, s20, #0, null
	.loc	1 86 24                         ; mm_baseline.py:86:24
	sl_sme_load_16x1b64_rowxfb16 s[32:35], s[4:5], 0x0, 0x0, 0x0, 0x1
	.loc	1 87 24                         ; mm_baseline.py:87:24
	sl_mov_b32 s2, s34
	sl_add_i32 s7, s5, 0x8000
	ml_slb_load_b32x1  v76, v67, s20, #0, null
	sl_sme_load_16x1b64_col s[0:3], s[6:7], 0x0, 0x0, 0x0, 0x1
	.loc	1 85 26                         ; mm_baseline.py:85:26
	sl_add_i64 s[0:1], s[0:1], 0x40
	sl_add_i32 s16, s16, 0xffffffff
	.loc	1 87 24                         ; mm_baseline.py:87:24
	ml_slb_load_b32x1  v77, v66, s21, #0, null
	.loc	1 85 26                         ; mm_baseline.py:85:26
	sl_cmp_eq_u32 wcr, s16, 0x0
	sl_add_i64 s[32:33], s[32:33], 0x40
	.loc	1 87 24                         ; mm_baseline.py:87:24
	ml_slb_load_b32x1  v78, v67, s21, #0, null
	.loc	1 93 26                         ; mm_baseline.py:93:26
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[71:72], v[73:74], v[0:3]
	.loc	1 87 24                         ; mm_baseline.py:87:24
	ml_slb_load_b32x1  v79, v66, s22, #0, null
	ml_slb_load_b32x1  v80, v67, s22, #0, null
	.loc	1 93 26                         ; mm_baseline.py:93:26
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[71:72], v[75:76], v[4:7]
	.loc	1 86 24                         ; mm_baseline.py:86:24
	ml_slb_load_b32x1  v81, v65, s23, #0, null
	ml_slb_load_b32x1  v82, v65, s23, #256, null
	.loc	1 93 26                         ; mm_baseline.py:93:26
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[71:72], v[77:78], v[8:11]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[71:72], v[79:80], v[12:15]
	.loc	1 86 24                         ; mm_baseline.py:86:24
	ml_slb_load_b32x1  v71, v65, s28, #0, null
	ml_slb_load_b32x1  v72, v65, s28, #256, null
	.loc	1 93 26                         ; mm_baseline.py:93:26
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[81:82], v[73:74], v[16:19]
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[81:82], v[75:76], v[20:23]
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[81:82], v[77:78], v[24:27]
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[81:82], v[79:80], v[28:31]
	.loc	1 86 24                         ; mm_baseline.py:86:24
	ml_slb_load_b32x1  v81, v65, s29, #0, null
	ml_slb_load_b32x1  v82, v65, s29, #256, null
	.loc	1 93 26                         ; mm_baseline.py:93:26
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[71:72], v[73:74], v[32:35]
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[71:72], v[75:76], v[36:39]
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[71:72], v[77:78], v[40:43]
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[71:72], v[79:80], v[44:47]
	.loc	1 86 24                         ; mm_baseline.py:86:24
	ml_slb_load_b32x1  v71, v70, s18, #512, null
	ml_slb_load_b32x1  v72, v70, s18, #768, null
	.loc	1 93 26                         ; mm_baseline.py:93:26
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[48:51], v[81:82], v[73:74], v[48:51]
	.loc	1 87 24                         ; mm_baseline.py:87:24
	ml_slb_load_b32x1  v73, v68, s19, #0, null
	ml_slb_load_b32x1  v74, v69, s19, #0, null
	.loc	1 93 26                         ; mm_baseline.py:93:26
	ml_matrix_mad_f32_bf16_m16n16k16 v[52:55], v[81:82], v[75:76], v[52:55]
	.loc	1 87 24                         ; mm_baseline.py:87:24
	ml_slb_load_b32x1  v75, v68, s20, #0, null
	ml_slb_load_b32x1  v76, v69, s20, #0, null
	.loc	1 93 26                         ; mm_baseline.py:93:26
	ml_matrix_mad_f32_bf16_m16n16k16 v[56:59], v[81:82], v[77:78], v[56:59]
	.loc	1 87 24                         ; mm_baseline.py:87:24
	ml_slb_load_b32x1  v77, v68, s21, #0, null
	ml_slb_load_b32x1  v78, v69, s21, #0, null
	.loc	1 93 26                         ; mm_baseline.py:93:26
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[81:82], v[79:80], v[60:63]
	.loc	1 87 24                         ; mm_baseline.py:87:24
	ml_slb_load_b32x1  v79, v68, s22, #0, null
	ml_slb_load_b32x1  v80, v69, s22, #0, null
	.loc	1 93 26                         ; mm_baseline.py:93:26
	sl_wait lmcnt(6)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[71:72], v[73:74], v[0:3]
	.loc	1 86 24                         ; mm_baseline.py:86:24
	ml_slb_load_b32x1  v81, v70, s23, #512, null
	ml_slb_load_b32x1  v82, v70, s23, #768, null
	.loc	1 93 26                         ; mm_baseline.py:93:26
	sl_wait lmcnt(6)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[71:72], v[75:76], v[4:7]
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[71:72], v[77:78], v[8:11]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[71:72], v[79:80], v[12:15]
	.loc	1 86 24                         ; mm_baseline.py:86:24
	ml_slb_load_b32x1  v71, v70, s28, #512, null
	ml_slb_load_b32x1  v72, v70, s28, #768, null
	.loc	1 93 26                         ; mm_baseline.py:93:26
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[81:82], v[73:74], v[16:19]
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[81:82], v[75:76], v[20:23]
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[81:82], v[77:78], v[24:27]
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[81:82], v[79:80], v[28:31]
	.loc	1 86 24                         ; mm_baseline.py:86:24
	ml_slb_load_b32x1  v81, v70, s29, #512, null
	ml_slb_load_b32x1  v82, v70, s29, #768, null
	.loc	1 93 26                         ; mm_baseline.py:93:26
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[71:72], v[73:74], v[32:35]
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[71:72], v[75:76], v[36:39]
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[71:72], v[77:78], v[40:43]
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[71:72], v[79:80], v[44:47]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[48:51], v[81:82], v[73:74], v[48:51]
	ml_matrix_mad_f32_bf16_m16n16k16 v[52:55], v[81:82], v[75:76], v[52:55]
	ml_matrix_mad_f32_bf16_m16n16k16 v[56:59], v[81:82], v[77:78], v[56:59]
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[81:82], v[79:80], v[60:63]
	.loc	1 85 26                         ; mm_baseline.py:85:26
	sl_cbr_wcrz BB0_2, wcr
; %bb.3:                                ; %._crit_edge.loopexit
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_cvt_bf16_f32  v93, v0
	ml_cvt_bf16_f32  v94, v1
	ml_cvt_bf16_f32  v95, v2
	ml_cvt_bf16_f32  v96, v3
	ml_cvt_bf16_f32  v89, v16
	ml_cvt_bf16_f32  v90, v17
	ml_cvt_bf16_f32  v91, v18
	ml_cvt_bf16_f32  v92, v19
	ml_cvt_bf16_f32  v81, v32
	ml_cvt_bf16_f32  v82, v33
	ml_cvt_bf16_f32  v83, v34
	ml_cvt_bf16_f32  v86, v35
	ml_cvt_bf16_f32  v84, v48
	ml_cvt_bf16_f32  v87, v49
	ml_cvt_bf16_f32  v85, v50
	ml_cvt_bf16_f32  v88, v51
	ml_cvt_bf16_f32  v73, v4
	ml_cvt_bf16_f32  v74, v5
	ml_cvt_bf16_f32  v75, v6
	ml_cvt_bf16_f32  v78, v7
	ml_cvt_bf16_f32  v76, v20
	ml_cvt_bf16_f32  v79, v21
	ml_cvt_bf16_f32  v77, v22
	ml_cvt_bf16_f32  v80, v23
	ml_cvt_bf16_f32  v65, v36
	ml_cvt_bf16_f32  v66, v37
	ml_cvt_bf16_f32  v67, v38
	ml_cvt_bf16_f32  v70, v39
	ml_cvt_bf16_f32  v68, v52
	ml_cvt_bf16_f32  v71, v53
	ml_cvt_bf16_f32  v69, v54
	ml_cvt_bf16_f32  v72, v55
	ml_cvt_bf16_f32  v48, v8
	ml_cvt_bf16_f32  v49, v9
	ml_cvt_bf16_f32  v50, v10
	ml_cvt_bf16_f32  v53, v11
	ml_cvt_bf16_f32  v51, v24
	ml_cvt_bf16_f32  v54, v25
	ml_cvt_bf16_f32  v52, v26
	ml_cvt_bf16_f32  v55, v27
	ml_cvt_bf16_f32  v32, v40
	ml_cvt_bf16_f32  v33, v41
	ml_cvt_bf16_f32  v34, v42
	ml_cvt_bf16_f32  v37, v43
	ml_cvt_bf16_f32  v35, v56
	ml_cvt_bf16_f32  v38, v57
	ml_cvt_bf16_f32  v36, v58
	ml_cvt_bf16_f32  v39, v59
	ml_cvt_bf16_f32  v21, v12
	ml_cvt_bf16_f32  v23, v13
	ml_cvt_bf16_f32  v24, v14
	ml_cvt_bf16_f32  v27, v15
	ml_cvt_bf16_f32  v22, v28
	ml_cvt_bf16_f32  v25, v29
	ml_cvt_bf16_f32  v26, v30
	ml_cvt_bf16_f32  v28, v31
	ml_cvt_bf16_f32  v13, v44
	ml_cvt_bf16_f32  v15, v45
	ml_cvt_bf16_f32  v17, v46
	ml_cvt_bf16_f32  v19, v47
	ml_cvt_bf16_f32  v14, v60
	ml_cvt_bf16_f32  v16, v61
	ml_cvt_bf16_f32  v18, v62
	ml_cvt_bf16_f32  v20, v63
BB0_4:                                  ; %._crit_edge
	.loc	1 71 44                         ; mm_baseline.py:71:44
	ml_shl_b32 v31, v64, 0x1
	ml_and_b32 v0, v31, 0xe
	sl_srl_b32 {s0, wcr}, s12, 0x2
	.loc	1 77 31                         ; mm_baseline.py:77:31
	sl_add_i32 s0, s13, s0
	ml_add_i32 v40, s0, v0
	ml_add_i32 v29, v40, 0xc0
	ml_add_i32 v30, v40, 0x80
	ml_add_i32 v41, v40, 0x40
	.loc	1 71 44                         ; mm_baseline.py:71:44
	ml_bfe2_b32 v0, v64, 0x63
	sl_srl_b32 {s0, wcr}, s8, 0x4
	sl_and_b32 {s0, wcr}, s0, 0x30
	.loc	1 71 31 is_stmt 0               ; mm_baseline.py:71:31
	sl_add_i32 s0, s9, s0
	ml_add_i32 v12, s0, v0
	ml_add_i32 v42, v12, 0xc8
	ml_add_i32 v43, v12, 0xc0
	ml_add_i32 v44, v12, 0x88
	ml_add_i32 v45, v12, 0x80
	ml_add_i32 v46, v12, 0x48
	ml_add_i32 v47, v12, 0x40
	ml_add_i32 v56, v12, 0x8
	.loc	1 85 26 is_stmt 1               ; mm_baseline.py:85:26
	sl_wait g2scnt(0)
	sl_barrier 
	.loc	1 140 31                        ; mm_baseline.py:140:31
	ml_mul_u64_u32 v[10:11], s31, v12
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_mov_b32 s30, 0x1000504
	sl_mov_b32 s32, 0x2010200
	.loc	1 140 31                        ; mm_baseline.py:140:31
	ml_mul_u64_u32 v[8:9], s31, v56
	ml_mul_u64_u32 v[5:6], s31, v47
	ml_mul_u64_u32 v[6:7], s31, v46
	ml_mul_u64_u32 v[2:3], s31, v45
	ml_mul_u64_u32 v[3:4], s31, v44
	ml_mul_u64_u32 v[0:1], s31, v43
	.loc	1 140 43 is_stmt 0              ; mm_baseline.py:140:43
	ml_add_i32 v1, v40, v10
	.loc	1 140 17                        ; mm_baseline.py:140:17
	ml_sra_b32 v4, v1, 0x1f
	ml_shl_b32 v7, v1, 0x1
	ml_shl_b32 v4, v4, 0x1
	ml_addo_u32 {v7, tcr}, s24, v7
	ml_srl_b32 v9, v1, 0x1f
	ml_or_b32 v4, v4, v9
	ml_mov_b32 v9, s25
	ml_addc_i32 v4, v9, v4, tcr
	.loc	1 141 17 is_stmt 1              ; mm_baseline.py:141:17
	ml_cmp_gt_i32 tcr, s26, v12
	.loc	1 140 31                        ; mm_baseline.py:140:31
	ml_mul_u64_u32 v[11:12], s31, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	sl_mov_b32 s31, s34
	.loc	1 141 17                        ; mm_baseline.py:141:17
	sl_mov_b64 s[6:7], tcr
	ml_cmp_gt_i32 tcr, s26, v56
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v9, v94, v93, s30
	ml_byte_permute_b32 v12, v96, v95, s30
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_mov_v2s_b32 s28, v7, 0x0
	.loc	1 141 17                        ; mm_baseline.py:141:17
	sl_mov_b64 s[4:5], tcr
	ml_cmp_gt_i32 tcr, s26, v47
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_and_b32 v47, tid, 0x20
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_mov_v2s_b32 s29, v4, 0x0
	ml_mov_b32 v4, s28
	.loc	1 141 17                        ; mm_baseline.py:141:17
	sl_mov_b64 s[2:3], tcr
	ml_cmp_gt_i32 tcr, s26, v46
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_bfe2_b32 v46, tid, 0x25
	ml_anyop3_b32 v31, 62, v31, v46, 0xfffffff8
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v4, v7, v4
	.loc	1 141 17                        ; mm_baseline.py:141:17
	sl_mov_b64 s[0:1], tcr
	ml_cmp_gt_i32 tcr, s26, v45
	sl_mov_b64 s[18:19], tcr
	ml_cmp_gt_i32 tcr, s26, v44
	sl_mov_b64 s[14:15], tcr
	ml_cmp_gt_i32 tcr, s26, v43
	ml_mov_b32 v43, 0x5410
	sl_mov_b64 s[12:13], tcr
	ml_cmp_gt_i32 tcr, s26, v42
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_and_b32 v42, tid, 0x1
	.loc	1 141 17                        ; mm_baseline.py:141:17
	sl_mov_b64 s[8:9], tcr
	.loc	1 141 37 is_stmt 0              ; mm_baseline.py:141:37
	ml_cmp_gt_i32 tcr, s27, v40
	sl_mov_b64 s[24:25], tcr
	ml_cmp_gt_i32 tcr, s27, v41
	sl_mov_b64 s[22:23], tcr
	ml_cmp_gt_i32 tcr, s27, v30
	sl_mov_b64 s[20:21], tcr
	ml_cmp_gt_i32 tcr, s27, v29
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[26:27], wcr}, s[6:7], s[24:25]
	.loc	1 141 37                        ; mm_baseline.py:141:37
	sl_mov_b64 s[16:17], tcr
	.loc	1 131 17 is_stmt 1              ; mm_baseline.py:131:17
	ml_cmp_eq_u32 tcr, v42, 0x0
	ml_mov_b32 v42, 0x7632
	ml_csel_b32 v44, v43, v42, tcr
	ml_byte_permute_b32 v44, v44, v44, s32
	ml_pk_shl_b16 v44, v44, 0x40004
	ml_pk_srl_b8 v44, v44, 0x40004
	ml_byte_permute_b32 v45, v9, v12, v44
	ml_slb_shuffle_rtn_b32 v45, v45, v31
	ml_csel_b32 v46, v42, v43, tcr
	ml_byte_permute_b32 v46, v46, v46, s32
	ml_pk_shl_b16 v46, v46, 0x40004
	ml_pk_srl_b8 v46, v46, 0x40004
	ml_byte_permute_b32 v9, v9, v12, v46
	ml_xor_b32 v12, v31, 0x1
	ml_slb_shuffle_rtn_b32 v9, v9, v12
	ml_cmp_eq_u32 tcr, v47, 0x0
	ml_mov_b32 v47, 0x1054
	ml_csel_b32 v43, v43, v47, tcr
	ml_byte_permute_b32 v43, v43, v43, s32
	ml_pk_shl_b16 v43, v43, 0x40004
	ml_pk_srl_b8 v43, v43, 0x40004
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v7, v45, v9, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[26:27], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v4, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v90, v89, s30
	ml_byte_permute_b32 v47, v92, v91, s30
	ml_byte_permute_b32 v56, v7, v47, v44
	ml_slb_shuffle_rtn_b32 v56, v56, v31
	ml_byte_permute_b32 v7, v7, v47, v46
	ml_mov_b32 v47, 0x3276
	ml_csel_b32 v42, v42, v47, tcr
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v47, v40, v8
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v47, v47, v1
	ml_shl_b32 v47, v47, 0x1
	ml_mov_v2s_b32 s33, v47, 0x0
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[26:27], wcr}, s[4:5], s[24:25]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_slb_shuffle_rtn_b32 v7, v7, v12
	ml_byte_permute_b32 v42, v42, v42, s32
	ml_pk_shl_b16 v42, v42, 0x40004
	ml_pk_srl_b8 v42, v42, 0x40004
	ml_byte_permute_b32 v9, v45, v9, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v45, s33, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[26:27], tmsk
	ml_lsa_store_dword v9, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v9, v40, v5
	ml_add_i32 v45, v40, v6
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[26:27], wcr}, s[2:3], s[24:25]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v9, v9, v1
	ml_shl_b32 v9, v9, 0x1
	ml_mov_v2s_b32 s32, v9, 0x0
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v9, v56, v7, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v45, v45, v1
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s33, v45, 0x0
	ml_add_i32 v45, s32, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[26:27], tmsk
	ml_lsa_store_dword v9, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[26:27], wcr}, s[0:1], s[24:25]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v56, v7, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v9, s33, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[26:27], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v82, v81, s30
	ml_byte_permute_b32 v9, v86, v83, s30
	ml_byte_permute_b32 v45, v7, v9, v44
	ml_slb_shuffle_rtn_b32 v45, v45, v31
	ml_byte_permute_b32 v47, v87, v84, s30
	ml_byte_permute_b32 v7, v7, v9, v46
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v9, v40, v2
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_slb_shuffle_rtn_b32 v7, v7, v12
	ml_byte_permute_b32 v56, v88, v85, s30
	ml_byte_permute_b32 v57, v47, v56, v44
	ml_byte_permute_b32 v47, v47, v56, v46
	ml_slb_shuffle_rtn_b32 v57, v57, v31
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v56, v40, v3
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[26:27], wcr}, s[18:19], s[24:25]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v9, v9, v1
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_slb_shuffle_rtn_b32 v47, v47, v12
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_shl_b32 v9, v9, 0x1
	ml_mov_v2s_b32 s32, v9, 0x0
	ml_sub_i32 v56, v56, v1
	ml_shl_b32 v56, v56, 0x1
	ml_mov_v2s_b32 s33, v56, 0x0
	ml_add_i32 v56, s32, v4
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v9, v45, v7, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[26:27], tmsk
	ml_lsa_store_dword v9, s[28:31], signed v56, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[26:27], wcr}, s[14:15], s[24:25]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v45, v7, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v9, s33, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[26:27], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v7, v40, v0
	ml_add_i32 v9, v40, v11
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[26:27], wcr}, s[12:13], s[24:25]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v7, v7, v1
	ml_shl_b32 v7, v7, 0x1
	ml_mov_v2s_b32 s32, v7, 0x0
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v7, v57, v47, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v9, v9, v1
	ml_shl_b32 v9, v9, 0x1
	ml_mov_v2s_b32 s33, v9, 0x0
	ml_add_i32 v9, s32, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[26:27], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[24:25], wcr}, s[8:9], s[24:25]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v57, v47, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v9, s33, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v74, v73, s30
	ml_byte_permute_b32 v9, v78, v75, s30
	ml_byte_permute_b32 v40, v7, v9, v44
	ml_slb_shuffle_rtn_b32 v40, v40, v31
	ml_byte_permute_b32 v45, v79, v76, s30
	ml_byte_permute_b32 v7, v7, v9, v46
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v9, v41, v10
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_slb_shuffle_rtn_b32 v7, v7, v12
	ml_byte_permute_b32 v47, v80, v77, s30
	ml_byte_permute_b32 v56, v45, v47, v44
	ml_byte_permute_b32 v45, v45, v47, v46
	ml_slb_shuffle_rtn_b32 v56, v56, v31
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v47, v41, v8
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[24:25], wcr}, s[6:7], s[22:23]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v9, v9, v1
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_slb_shuffle_rtn_b32 v45, v45, v12
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_shl_b32 v9, v9, 0x1
	ml_mov_v2s_b32 s26, v9, 0x0
	ml_sub_i32 v47, v47, v1
	ml_shl_b32 v47, v47, 0x1
	ml_mov_v2s_b32 s27, v47, 0x0
	ml_add_i32 v47, s26, v4
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v9, v40, v7, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v9, s[28:31], signed v47, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[24:25], wcr}, s[4:5], s[22:23]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v40, v7, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v9, s27, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v7, v41, v5
	ml_add_i32 v9, v41, v6
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[24:25], wcr}, s[2:3], s[22:23]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v7, v7, v1
	ml_shl_b32 v7, v7, 0x1
	ml_mov_v2s_b32 s26, v7, 0x0
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v7, v56, v45, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v9, v9, v1
	ml_shl_b32 v9, v9, 0x1
	ml_mov_v2s_b32 s27, v9, 0x0
	ml_add_i32 v9, s26, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[24:25], wcr}, s[0:1], s[22:23]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v56, v45, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v9, s27, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v66, v65, s30
	ml_byte_permute_b32 v9, v70, v67, s30
	ml_byte_permute_b32 v40, v7, v9, v44
	ml_slb_shuffle_rtn_b32 v40, v40, v31
	ml_byte_permute_b32 v45, v71, v68, s30
	ml_byte_permute_b32 v7, v7, v9, v46
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v9, v41, v2
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_slb_shuffle_rtn_b32 v7, v7, v12
	ml_byte_permute_b32 v47, v72, v69, s30
	ml_byte_permute_b32 v56, v45, v47, v44
	ml_byte_permute_b32 v45, v45, v47, v46
	ml_slb_shuffle_rtn_b32 v56, v56, v31
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v47, v41, v3
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[24:25], wcr}, s[18:19], s[22:23]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v9, v9, v1
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_slb_shuffle_rtn_b32 v45, v45, v12
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_shl_b32 v9, v9, 0x1
	ml_mov_v2s_b32 s26, v9, 0x0
	ml_sub_i32 v47, v47, v1
	ml_shl_b32 v47, v47, 0x1
	ml_mov_v2s_b32 s27, v47, 0x0
	ml_add_i32 v47, s26, v4
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v9, v40, v7, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v9, s[28:31], signed v47, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[24:25], wcr}, s[14:15], s[22:23]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v40, v7, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v9, s27, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v7, v41, v0
	ml_add_i32 v9, v41, v11
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[24:25], wcr}, s[12:13], s[22:23]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v7, v7, v1
	ml_shl_b32 v7, v7, 0x1
	ml_mov_v2s_b32 s26, v7, 0x0
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v7, v56, v45, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v9, v9, v1
	ml_shl_b32 v9, v9, 0x1
	ml_mov_v2s_b32 s27, v9, 0x0
	ml_add_i32 v9, s26, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[22:23], wcr}, s[8:9], s[22:23]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v56, v45, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v9, s27, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v49, v48, s30
	ml_byte_permute_b32 v9, v53, v50, s30
	ml_byte_permute_b32 v40, v7, v9, v44
	ml_slb_shuffle_rtn_b32 v40, v40, v31
	ml_byte_permute_b32 v41, v54, v51, s30
	ml_byte_permute_b32 v7, v7, v9, v46
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v9, v30, v10
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_slb_shuffle_rtn_b32 v7, v7, v12
	ml_byte_permute_b32 v45, v55, v52, s30
	ml_byte_permute_b32 v47, v41, v45, v44
	ml_byte_permute_b32 v41, v41, v45, v46
	ml_slb_shuffle_rtn_b32 v47, v47, v31
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v45, v30, v8
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[22:23], wcr}, s[6:7], s[20:21]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v9, v9, v1
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_slb_shuffle_rtn_b32 v41, v41, v12
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_shl_b32 v9, v9, 0x1
	ml_mov_v2s_b32 s24, v9, 0x0
	ml_sub_i32 v45, v45, v1
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s25, v45, 0x0
	ml_add_i32 v45, s24, v4
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v9, v40, v7, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v9, s[28:31], signed v45, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[22:23], wcr}, s[4:5], s[20:21]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v40, v7, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v9, s25, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v7, v30, v5
	ml_add_i32 v9, v30, v6
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[22:23], wcr}, s[2:3], s[20:21]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v7, v7, v1
	ml_shl_b32 v7, v7, 0x1
	ml_mov_v2s_b32 s24, v7, 0x0
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v7, v47, v41, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v9, v9, v1
	ml_shl_b32 v9, v9, 0x1
	ml_mov_v2s_b32 s25, v9, 0x0
	ml_add_i32 v9, s24, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[22:23], wcr}, s[0:1], s[20:21]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v47, v41, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v9, s25, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v33, v32, s30
	ml_byte_permute_b32 v9, v37, v34, s30
	ml_byte_permute_b32 v32, v7, v9, v44
	ml_slb_shuffle_rtn_b32 v32, v32, v31
	ml_byte_permute_b32 v33, v38, v35, s30
	ml_byte_permute_b32 v7, v7, v9, v46
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v9, v30, v2
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_slb_shuffle_rtn_b32 v7, v7, v12
	ml_byte_permute_b32 v34, v39, v36, s30
	ml_byte_permute_b32 v35, v33, v34, v44
	ml_byte_permute_b32 v33, v33, v34, v46
	ml_slb_shuffle_rtn_b32 v35, v35, v31
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v34, v30, v3
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[22:23], wcr}, s[18:19], s[20:21]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v9, v9, v1
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_slb_shuffle_rtn_b32 v33, v33, v12
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_shl_b32 v9, v9, 0x1
	ml_mov_v2s_b32 s24, v9, 0x0
	ml_sub_i32 v34, v34, v1
	ml_shl_b32 v34, v34, 0x1
	ml_mov_v2s_b32 s25, v34, 0x0
	ml_add_i32 v34, s24, v4
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v9, v32, v7, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v9, s[28:31], signed v34, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[22:23], wcr}, s[14:15], s[20:21]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v32, v7, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v9, s25, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v7, v30, v0
	ml_add_i32 v9, v30, v11
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[22:23], wcr}, s[12:13], s[20:21]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v7, v7, v1
	ml_shl_b32 v7, v7, 0x1
	ml_mov_v2s_b32 s24, v7, 0x0
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v7, v35, v33, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v9, v9, v1
	ml_shl_b32 v9, v9, 0x1
	ml_mov_v2s_b32 s25, v9, 0x0
	ml_add_i32 v9, s24, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[20:21], wcr}, s[8:9], s[20:21]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v35, v33, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v9, s25, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[20:21], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v23, v21, s30
	ml_byte_permute_b32 v9, v27, v24, s30
	ml_byte_permute_b32 v21, v7, v9, v44
	ml_slb_shuffle_rtn_b32 v21, v21, v31
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v10, v29, v10
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v7, v9, v46
	ml_byte_permute_b32 v9, v25, v22, s30
	ml_slb_shuffle_rtn_b32 v7, v7, v12
	ml_byte_permute_b32 v22, v28, v26, s30
	ml_byte_permute_b32 v23, v9, v22, v44
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v8, v29, v8
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_slb_shuffle_rtn_b32 v23, v23, v31
	ml_byte_permute_b32 v9, v9, v22, v46
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[6:7], wcr}, s[6:7], s[16:17]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v10, v10, v1
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_slb_shuffle_rtn_b32 v9, v9, v12
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_shl_b32 v10, v10, 0x1
	ml_mov_v2s_b32 s20, v10, 0x0
	ml_sub_i32 v8, v8, v1
	ml_shl_b32 v8, v8, 0x1
	ml_mov_v2s_b32 s21, v8, 0x0
	ml_add_i32 v8, s20, v4
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v10, v21, v7, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v10, s[28:31], signed v8, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[4:5], wcr}, s[4:5], s[16:17]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v7, v21, v7, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v8, s21, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v7, s[28:31], signed v8, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v5, v29, v5
	ml_add_i32 v6, v29, v6
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[2:3], wcr}, s[2:3], s[16:17]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v5, v5, v1
	ml_shl_b32 v5, v5, 0x1
	ml_mov_v2s_b32 s4, v5, 0x0
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v5, v23, v9, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v6, v6, v1
	ml_shl_b32 v6, v6, 0x1
	ml_mov_v2s_b32 s5, v6, 0x0
	ml_add_i32 v6, s4, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[2:3], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v6, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[0:1], wcr}, s[0:1], s[16:17]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v5, v23, v9, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v6, s5, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v5, s[28:31], signed v6, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v5, v15, v13, s30
	ml_byte_permute_b32 v6, v19, v17, s30
	ml_byte_permute_b32 v7, v5, v6, v44
	ml_slb_shuffle_rtn_b32 v7, v7, v31
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v2, v29, v2
	ml_add_i32 v3, v29, v3
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v5, v5, v6, v46
	ml_slb_shuffle_rtn_b32 v5, v5, v12
	ml_byte_permute_b32 v6, v16, v14, s30
	ml_byte_permute_b32 v8, v20, v18, s30
	ml_byte_permute_b32 v9, v6, v8, v44
	ml_slb_shuffle_rtn_b32 v9, v9, v31
	.loc	1 140 43                        ; mm_baseline.py:140:43
	ml_add_i32 v0, v29, v0
	ml_add_i32 v10, v29, v11
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v6, v6, v8, v46
	ml_slb_shuffle_rtn_b32 v6, v6, v12
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[0:1], wcr}, s[18:19], s[16:17]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_sub_i32 v2, v2, v1
	ml_shl_b32 v2, v2, 0x1
	ml_mov_v2s_b32 s2, v2, 0x0
	ml_sub_i32 v3, v3, v1
	ml_shl_b32 v3, v3, 0x1
	ml_mov_v2s_b32 s3, v3, 0x0
	ml_add_i32 v3, s2, v4
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v2, v7, v5, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v2, s[28:31], signed v3, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[0:1], wcr}, s[14:15], s[16:17]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v2, v7, v5, v42
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v3, s3, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v2, s[28:31], signed v3, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	ml_sub_i32 v0, v0, v1
	ml_shl_b32 v0, v0, 0x1
	ml_mov_v2s_b32 s2, v0, 0x0
	ml_sub_i32 v0, v10, v1
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[0:1], wcr}, s[12:13], s[16:17]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v1, v9, v6, v43
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_shl_b32 v0, v0, 0x1
	ml_mov_v2s_b32 s3, v0, 0x0
	ml_add_i32 v0, s2, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v1, s[28:31], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 131 17                        ; mm_baseline.py:131:17
	ml_byte_permute_b32 v0, v9, v6, v42
	.loc	1 141 31                        ; mm_baseline.py:141:31
	sl_and_b64 {s[0:1], wcr}, s[8:9], s[16:17]
	.loc	1 144 20                        ; mm_baseline.py:144:20
	ml_add_i32 v1, s3, v4
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v0, s[28:31], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 143 4                         ; mm_baseline.py:143:4
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
	.long	536856
	.asciz	"\003\000\264\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	mm_kernel, .Lfunc_end0-mm_kernel
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 7760
; NumSgprs: 40
; NumVgprs: 97
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 4
; VGPRBlocks: 24
; NumSGPRsForWarpsPerNU: 36
; NumVGPRsForWarpsPerNR: 97
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
	.long	197                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0xbe DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"mm_baseline.py"                ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/workspace/experiments/minicpm-s2/framework/20261021T173921Z-mm-cta-group-gate/source" ; DW_AT_comp_dir
	.byte	0
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.byte	2                               ; Abbrev [2] 0x8e:0xc DW_TAG_subprogram
	.ascii	"mm_kernel"                     ; DW_AT_name
	.byte	0
	.byte	1                               ; DW_AT_inline
	.byte	3                               ; Abbrev [3] 0x9a:0x2e DW_TAG_subprogram
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.long	142                             ; DW_AT_abstract_origin
	.byte	4                               ; Abbrev [4] 0xaf:0xc DW_TAG_inlined_subroutine
	.long	142                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges0                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	57                              ; DW_AT_call_line
	.byte	24                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0xbb:0xc DW_TAG_inlined_subroutine
	.long	142                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges1                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	85                              ; DW_AT_call_line
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
    .sgpr_count:     40
    .sgpr_spill_count: 0
    .symbol:         mm_kernel.kd
    .vgpr_count:     97
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
