	.text
	.globl	half_mm                         ; -- Begin function half_mm
	.p2align	3
	.type	half_mm,@function
	.iluvatar_kernel half_mm
half_mm:                                ; @half_mm
.Lfunc_begin0:
	.file	1 "/workspace/experiments/minicpm-s2/framework/20261026T075700478338Z-biv150-gate-partial-fusion-component/source" "candidate.py"
	.loc	1 8 0                           ; candidate.py:8:0
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
		granulated_workitem_vgpr_count = 42
		granulated_warp_sgpr_count = 9
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
		kernarg_segment_byte_size = 48
		workgroup_fbarrier_count = 0
		warp_sgpr_count = 80
		workitem_vgpr_count = 169
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
	sl_mov_b32 s74, tcr_lo
	ml_vrf_init_u32 v148, tcr
.Ltmp0:
	.loc	1 12 24 prologue_end            ; candidate.py:12:24
	sl_lsa_load_b32x16 s[12:27], s[4:5], noreg, #0, ca
	.loc	1 16 22                         ; candidate.py:16:22
	sl_mulh_u32 s0, s6, 0x2aaaaaab
	sl_srl_b32 {s1, wcr}, s0, 0x5
	.loc	1 17 37                         ; candidate.py:17:37
	sl_wait smcnt(0)
	sl_mull_u32 s21, s1, 0x8
	sl_mov_b32 s0, 0x8
	.loc	1 17 26 is_stmt 0               ; candidate.py:17:26
	sl_sub_i32 s7, s0, s21
	.loc	1 18 30 is_stmt 1               ; candidate.py:18:30
	sl_abs_i32 s10, s7
	ml_cvt_f32_u32  v0, s10
	sl_mov_b32 s20, 0x0
	ml_rcp_f32 v0, v0
	sl_reg_read s2, hwreg(HW_REG_MODE)
	sl_cmp_eq_u32 wcr, s7, 0x0
	sl_sub_bi_u32 s0, s8, s8, wcr
	sl_or_b32 {s3, wcr}, s2, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s3
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s2
	ml_mov_v2s_b32 s4, v0, 0x0
	.loc	1 19 16                         ; candidate.py:19:16
	sl_mull_u32 s1, s1, 0xffffff40
	sl_add_i32 s11, s1, s6
	ml_shl_b32 v150, v148, 0x2
	.loc	1 18 30                         ; candidate.py:18:30
	sl_mul_u64_u32 s[2:3], s4, s10
	sl_neg_i32 s1, s2
	sl_cmp_eq_u32 wcr, s3, 0x0
	sl_csel_b32 s1, s1, s2, wcr
	sl_mul_u64_u32 s[2:3], s1, s4
	sl_add_i32 s1, s4, s3
	sl_sub_i32 s2, s4, s3
	sl_csel_b32 s22, s1, s2, wcr
	sl_mul_u64_u32 s[2:3], s22, s6
	sl_mull_u32 s1, s3, s10
	sl_sub_i32 s23, s6, s1
	sl_cmp_ge_u32 wcr, s23, s10
	sl_sub_bi_u64 s[2:3], s[8:9], s[8:9], wcr
	sl_cmp_ge_u32 wcr, s6, s1
	sl_sub_bi_u32 s1, s8, s8, wcr
	sl_sub_bi_u64 s[4:5], s[8:9], s[8:9], wcr
	sl_and_b64 {s[4:5], wcr}, s[2:3], s[4:5]
	sl_mov_b32 s2, 0xffffffff
	sl_or_b32 {s4, wcr}, s4, s5
	sl_csel_b32 s3, s2, 0x0, wcr
	sl_cmp_eq_u32 wcr, s3, 0x0
	sl_sub_i32 s3, s23, s10
	sl_add_i32 s4, s23, s10
	sl_csel_b32 s3, s23, s3, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s3, s4, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s3, s2, s1, wcr
	.loc	1 19 26                         ; candidate.py:19:26
	sl_xor_b32 {s1, wcr}, s11, s7
	sl_sra_b32 {s23, wcr}, s1, 0x1f
	sl_abs_i32 s1, s11
	sl_mul_u64_u32 s[4:5], s22, s1
	sl_mull_u32 s4, s5, s10
	sl_sub_i32 s6, s1, s4
	sl_cmp_ge_u32 wcr, s6, s10
	sl_sub_bi_u64 s[6:7], s[8:9], s[8:9], wcr
	sl_cmp_ge_u32 wcr, s1, s4
	sl_sub_bi_u32 s1, s8, s8, wcr
	sl_sub_bi_u64 s[10:11], s[8:9], s[8:9], wcr
	sl_and_b64 {s[6:7], wcr}, s[6:7], s[10:11]
	sl_or_b32 {s6, wcr}, s6, s7
	sl_csel_b32 s4, s2, 0x0, wcr
	sl_cmp_eq_u32 wcr, s4, 0x0
	sl_add_i32 s4, s5, 0x1
	sl_add_i32 s6, s5, 0xffffffff
	sl_csel_b32 s4, s5, s4, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s4, s6, wcr
	sl_xor_b32 {s1, wcr}, s1, s23
	sl_sub_i32 s1, s1, s23
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s4, s2, s1, wcr
	.loc	1 18 24                         ; candidate.py:18:24
	sl_add_i32 s0, s3, s21
	.loc	1 20 14                         ; candidate.py:20:14
	sl_mull_u32 s21, s0, 0x100
	.loc	1 20 32 is_stmt 0               ; candidate.py:20:32
	sl_bfe2_b32 s5, tcr_lo, 0x86
	.loc	1 22 48 is_stmt 1               ; candidate.py:22:48
	sl_mulh_i32 s0, s21, 0x81228dbf
	sl_add_i32 s0, s0, s21
	sl_srl_b32 {s1, wcr}, s0, 0x1f
	sl_srl_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s1
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s0, s21, s0
	.loc	1 25 28                         ; candidate.py:25:28
	sl_mull_u32 s0, s0, 0x800
	.loc	1 25 13 is_stmt 0               ; candidate.py:25:13
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[0:1], s[12:13], s[0:1]
	sl_mov_b32 s3, 0x1000
	.loc	1 31 20 is_stmt 1               ; candidate.py:31:20
	sl_mull_u32 s13, s5, 0x400
	sl_mull_u32 s10, s5, 0x10000
	sl_mov_b32 s11, s13
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[10:11], 0x0, 0x0, 0x0, 0x1
	.loc	1 21 14                         ; candidate.py:21:14
	sl_mull_u32 s12, s4, 0x100
	.loc	1 23 48                         ; candidate.py:23:48
	sl_mulh_i32 s4, s12, 0x2aaaaaab
	sl_srl_b32 {s5, wcr}, s4, 0x1f
	sl_srl_b32 {s4, wcr}, s4, 0xa
	sl_add_i32 s4, s4, s5
	sl_mull_u32 s4, s4, 0x1800
	sl_sub_i32 s4, s12, s4
	.loc	1 26 42                         ; candidate.py:26:42
	sl_mull_u32 s4, s4, 0x800
	.loc	1 26 27 is_stmt 0               ; candidate.py:26:27
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x1
	sl_add_i64 s[14:15], s[14:15], s[4:5]
	.loc	1 28 14 is_stmt 1               ; candidate.py:28:14
	sl_add_i64 s[4:5], s[14:15], 0x1800000
	.loc	1 32 20                         ; candidate.py:32:20
	sl_mov_b64 s[6:7], s[2:3]
	sl_add_i32 s11, s13, 0x8000
	sl_sme_load_16x1b64_col s[4:7], s[10:11], 0x0, 0x0, 0x0, 0x1
	ml_shl_b32 v149, v148, 0x4
	ml_mov_v2s_b32 s4, v149, 0x0
	ml_and_b32 v64, v150, 0xcfc
	ml_shl_b32 v0, v148, 0x6
	ml_and_b32 v0, v0, 0x300
	sl_and_b32 {s4, wcr}, s4, 0xc00
	ml_and_b32 v1, v150, 0xfc
	ml_anyop3_b32 v65, s4, v0, v1, 0xfffffffe
	ml_xor_b32 v66, v65, 0x10
	ml_xor_b32 v67, v65, 0x20
	ml_xor_b32 v68, v65, 0x30
	.loc	1 30 19                         ; candidate.py:30:19
	sl_add_i64 s[4:5], s[14:15], 0x1800040
	sl_add_i64 s[0:1], s[0:1], 0x40
	sl_mov_b32 s14, 0x40
	ml_mov_b32 v40, 0x0
	ml_xor_b32 v69, v64, 0x80
	sl_mov_b32 s15, s2
	ml_mov_b32 v41, 0x0
	ml_mov_b32 v42, 0x0
	ml_mov_b32 v43, 0x0
	ml_mov_b32 v52, 0x0
	ml_mov_b32 v53, 0x0
	ml_mov_b32 v54, 0x0
	ml_mov_b32 v55, 0x0
	ml_mov_b32 v56, 0x0
	ml_mov_b32 v57, 0x0
	ml_mov_b32 v58, 0x0
	ml_mov_b32 v59, 0x0
	ml_mov_b32 v60, 0x0
	ml_mov_b32 v61, 0x0
	ml_mov_b32 v62, 0x0
	ml_mov_b32 v63, 0x0
	ml_mov_b32 v28, 0x0
	ml_mov_b32 v29, 0x0
	ml_mov_b32 v30, 0x0
	ml_mov_b32 v31, 0x0
	ml_mov_b32 v36, 0x0
	ml_mov_b32 v37, 0x0
	ml_mov_b32 v38, 0x0
	ml_mov_b32 v39, 0x0
	ml_mov_b32 v44, 0x0
	ml_mov_b32 v45, 0x0
	ml_mov_b32 v46, 0x0
	ml_mov_b32 v47, 0x0
	ml_mov_b32 v48, 0x0
	ml_mov_b32 v49, 0x0
	ml_mov_b32 v50, 0x0
	ml_mov_b32 v51, 0x0
	ml_mov_b32 v12, 0x0
	ml_mov_b32 v13, 0x0
	ml_mov_b32 v14, 0x0
	ml_mov_b32 v15, 0x0
	ml_mov_b32 v20, 0x0
	ml_mov_b32 v21, 0x0
	ml_mov_b32 v22, 0x0
	ml_mov_b32 v23, 0x0
	ml_mov_b32 v24, 0x0
	ml_mov_b32 v25, 0x0
	ml_mov_b32 v26, 0x0
	ml_mov_b32 v27, 0x0
	ml_mov_b32 v32, 0x0
	ml_mov_b32 v33, 0x0
	ml_mov_b32 v34, 0x0
	ml_mov_b32 v35, 0x0
	ml_mov_b32 v0, 0x0
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
	ml_mov_b32 v16, 0x0
	ml_mov_b32 v17, 0x0
	ml_mov_b32 v18, 0x0
	ml_mov_b32 v19, 0x0
BB0_1:                                  ; =>This Inner Loop Header: Depth=1
	sl_add_i32 s6, s15, 0x1
	sl_cmp_lt_i32 wcr, s6, 0x2
	sl_csel_b32 s15, s6, 0x0, wcr
	.loc	1 31 20                         ; candidate.py:31:20
	sl_wait g2scnt(0)
	sl_barrier_req 0x0
	sl_barrier_wait 0x0
	sl_mull_u32 s22, s15, 0x4000
	ml_slb_load_b32x1  v70, v64, s22, #0, null
	.loc	1 32 20                         ; candidate.py:32:20
	sl_add_i32 s23, s22, 0x8000
	sl_add_i32 s24, s22, 0x9000
	sl_add_i32 s25, s22, 0xa000
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v71, v64, s22, #256, null
	.loc	1 32 20                         ; candidate.py:32:20
	sl_add_i32 s26, s22, 0xb000
	.loc	1 31 20                         ; candidate.py:31:20
	sl_add_i32 s27, s22, 0x1000
	sl_add_i32 s28, s22, 0x2000
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v72, v65, s23, #0, null
	.loc	1 31 20                         ; candidate.py:31:20
	sl_add_i32 s29, s22, 0x3000
	.loc	1 30 19                         ; candidate.py:30:19
	sl_add_i32 s6, s20, 0x1
	sl_cmp_lt_i32 wcr, s6, 0x2
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v73, v66, s23, #0, null
	.loc	1 30 19                         ; candidate.py:30:19
	sl_csel_b32 s20, s6, 0x0, wcr
	.loc	1 31 20                         ; candidate.py:31:20
	sl_mull_u32 s6, s20, 0x4000
	sl_add_i32 s11, s13, s6
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v74, v65, s24, #0, null
	.loc	1 31 20                         ; candidate.py:31:20
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[10:11], 0x0, 0x0, 0x0, 0x1
	.loc	1 32 20                         ; candidate.py:32:20
	sl_mov_b64 s[6:7], s[2:3]
	sl_add_i32 s11, s11, 0x8000
	ml_slb_load_b32x1  v75, v66, s24, #0, null
	sl_sme_load_16x1b64_col s[4:7], s[10:11], 0x0, 0x0, 0x0, 0x1
	.loc	1 30 19                         ; candidate.py:30:19
	sl_add_i64 s[4:5], s[4:5], 0x40
	sl_add_i32 s14, s14, 0xffffffff
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v76, v65, s25, #0, null
	.loc	1 30 19                         ; candidate.py:30:19
	sl_cmp_eq_u32 wcr, s14, 0x0
	sl_add_i64 s[0:1], s[0:1], 0x40
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v77, v66, s25, #0, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[70:71], v[72:73], v[40:43]
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v78, v65, s26, #0, null
	ml_slb_load_b32x1  v79, v66, s26, #0, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[70:71], v[74:75], v[28:31]
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v80, v64, s27, #0, null
	ml_slb_load_b32x1  v81, v64, s27, #256, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[70:71], v[76:77], v[12:15]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[70:71], v[78:79], v[0:3]
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v70, v64, s28, #0, null
	ml_slb_load_b32x1  v71, v64, s28, #256, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[52:55], v[80:81], v[72:73], v[52:55]
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[80:81], v[74:75], v[36:39]
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[80:81], v[76:77], v[20:23]
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[80:81], v[78:79], v[4:7]
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v80, v64, s29, #0, null
	ml_slb_load_b32x1  v81, v64, s29, #256, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[56:59], v[70:71], v[72:73], v[56:59]
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[70:71], v[74:75], v[44:47]
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[70:71], v[76:77], v[24:27]
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[70:71], v[78:79], v[8:11]
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v70, v69, s22, #512, null
	ml_slb_load_b32x1  v71, v69, s22, #768, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[80:81], v[72:73], v[60:63]
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v72, v67, s23, #0, null
	ml_slb_load_b32x1  v73, v68, s23, #0, null
	.loc	1 34 25                         ; candidate.py:34:25
	ml_matrix_mad_f32_bf16_m16n16k16 v[48:51], v[80:81], v[74:75], v[48:51]
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v74, v67, s24, #0, null
	ml_slb_load_b32x1  v75, v68, s24, #0, null
	.loc	1 34 25                         ; candidate.py:34:25
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[80:81], v[76:77], v[32:35]
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v76, v67, s25, #0, null
	ml_slb_load_b32x1  v77, v68, s25, #0, null
	.loc	1 34 25                         ; candidate.py:34:25
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[80:81], v[78:79], v[16:19]
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v78, v67, s26, #0, null
	ml_slb_load_b32x1  v79, v68, s26, #0, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(6)
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[70:71], v[72:73], v[40:43]
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v80, v69, s27, #512, null
	ml_slb_load_b32x1  v81, v69, s27, #768, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(6)
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[70:71], v[74:75], v[28:31]
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[70:71], v[76:77], v[12:15]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[70:71], v[78:79], v[0:3]
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v70, v69, s28, #512, null
	ml_slb_load_b32x1  v71, v69, s28, #768, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[52:55], v[80:81], v[72:73], v[52:55]
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[80:81], v[74:75], v[36:39]
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[80:81], v[76:77], v[20:23]
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[80:81], v[78:79], v[4:7]
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v80, v69, s29, #512, null
	ml_slb_load_b32x1  v81, v69, s29, #768, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[56:59], v[70:71], v[72:73], v[56:59]
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[70:71], v[74:75], v[44:47]
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[70:71], v[76:77], v[24:27]
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[70:71], v[78:79], v[8:11]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[80:81], v[72:73], v[60:63]
	ml_matrix_mad_f32_bf16_m16n16k16 v[48:51], v[80:81], v[74:75], v[48:51]
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[80:81], v[76:77], v[32:35]
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[80:81], v[78:79], v[16:19]
	.loc	1 30 19                         ; candidate.py:30:19
	sl_cbr_wcrz BB0_1, wcr
; %bb.2:
	.loc	1 20 32                         ; candidate.py:20:32
	sl_bfe2_b32 s0, s74, 0x67
	ml_shl_b32 v64, v148, 0x1
	.loc	1 20 19 is_stmt 0               ; candidate.py:20:19
	sl_add_i32 s0, s21, s0
	.loc	1 21 19 is_stmt 1               ; candidate.py:21:19
	ml_mov_b32 v65, 0xfe
	ml_anyop3_b32 v145, s12, v64, v65, 0xffffffea
	.loc	1 30 19                         ; candidate.py:30:19
	sl_wait g2scnt(0)
	sl_barrier 
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s0, 0x7ee
	sl_sub_bi_u64 s[4:5], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s0, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v64, s1, v145
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 1               ; candidate.py:42:36
	ml_mov_b32 v162, 0x0
	ml_mov_b32 v161, 0x0
	ml_sra_b32 v65, v64, 0x1f
	ml_shl_b32 v164, v64, 0x1
	ml_shl_b32 v65, v65, 0x1
	ml_srl_b32 v66, v64, 0x1f
	ml_or_b32 v163, v65, v66
	sl_cbr_wcrz BB0_4, wcr
; %bb.3:
	.loc	1 0 36 is_stmt 0                ; candidate.py:0:36
	ml_addo_u32 {v65, tcr}, s16, v164
	ml_mov_b32 v66, s17
	ml_addc_i32 v66, v66, v163, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v65, v[65:66], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v161, v65, 0xffff0000
	ml_shl_b32 v162, v65, 0x10
BB0_4:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0x8
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[6:7], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v65, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v66, v65, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v160, 0x0
	ml_mov_b32 v159, 0x0
	sl_cbr_wcrz BB0_6, wcr
; %bb.5:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v67, v65, 0x1
	ml_shl_b32 v68, v66, 0x1
	ml_addo_u32 {v66, tcr}, s16, v67
	ml_srl_b32 v67, v65, 0x1f
	ml_or_b32 v67, v68, v67
	ml_mov_b32 v68, s17
	ml_addc_i32 v67, v68, v67, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v66, v[66:67], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v159, v66, 0xffff0000
	ml_shl_b32 v160, v66, 0x10
BB0_6:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0x10
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[10:11], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v66, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v67, v66, 0x1f
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v158, 0x0
	ml_mov_b32 v157, 0x0
	sl_cbr_wcrz BB0_8, wcr
; %bb.7:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v68, v66, 0x1
	ml_shl_b32 v69, v67, 0x1
	ml_addo_u32 {v67, tcr}, s16, v68
	ml_srl_b32 v68, v66, 0x1f
	ml_or_b32 v68, v69, v68
	ml_mov_b32 v69, s17
	ml_addc_i32 v68, v69, v68, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v67, v[67:68], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v157, v67, 0xffff0000
	ml_shl_b32 v158, v67, 0x10
BB0_8:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0x18
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[12:13], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v67, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v68, v67, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v156, 0x0
	ml_mov_b32 v155, 0x0
	sl_cbr_wcrz BB0_10, wcr
; %bb.9:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v69, v67, 0x1
	ml_shl_b32 v70, v68, 0x1
	ml_addo_u32 {v68, tcr}, s16, v69
	ml_srl_b32 v69, v67, 0x1f
	ml_or_b32 v69, v70, v69
	ml_mov_b32 v70, s17
	ml_addc_i32 v69, v70, v69, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v68, v[68:69], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v155, v68, 0xffff0000
	ml_shl_b32 v156, v68, 0x10
BB0_10:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0x20
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[14:15], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v68, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v69, v68, 0x1f
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v154, 0x0
	ml_mov_b32 v153, 0x0
	sl_cbr_wcrz BB0_12, wcr
; %bb.11:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v70, v68, 0x1
	ml_shl_b32 v71, v69, 0x1
	ml_addo_u32 {v69, tcr}, s16, v70
	ml_srl_b32 v70, v68, 0x1f
	ml_or_b32 v70, v71, v70
	ml_mov_b32 v71, s17
	ml_addc_i32 v70, v71, v70, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v69, v[69:70], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v153, v69, 0xffff0000
	ml_shl_b32 v154, v69, 0x10
BB0_12:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0x28
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[26:27], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v72, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v69, v72, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v152, 0x0
	ml_mov_b32 v151, 0x0
	sl_cbr_wcrz BB0_14, wcr
; %bb.13:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v70, v72, 0x1
	ml_shl_b32 v71, v69, 0x1
	ml_addo_u32 {v69, tcr}, s16, v70
	ml_srl_b32 v70, v72, 0x1f
	ml_or_b32 v70, v71, v70
	ml_mov_b32 v71, s17
	ml_addc_i32 v70, v71, v70, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v69, v[69:70], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v151, v69, 0xffff0000
	ml_shl_b32 v152, v69, 0x10
BB0_14:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0x30
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[20:21], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v69, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v70, v69, 0x1f
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v85, 0x0
	ml_mov_b32 v82, 0x0
	sl_cbr_wcrz BB0_16, wcr
; %bb.15:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v71, v69, 0x1
	ml_shl_b32 v73, v70, 0x1
	ml_addo_u32 {v70, tcr}, s16, v71
	ml_srl_b32 v71, v69, 0x1f
	ml_or_b32 v71, v73, v71
	ml_mov_b32 v73, s17
	ml_addc_i32 v71, v73, v71, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v70, v[70:71], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v82, v70, 0xffff0000
	ml_shl_b32 v85, v70, 0x10
BB0_16:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0x38
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[28:29], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v73, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v70, v73, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v88, 0x0
	ml_mov_b32 v86, 0x0
	sl_cbr_wcrz BB0_18, wcr
; %bb.17:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v71, v73, 0x1
	ml_shl_b32 v74, v70, 0x1
	ml_addo_u32 {v70, tcr}, s16, v71
	ml_srl_b32 v71, v73, 0x1f
	ml_or_b32 v71, v74, v71
	ml_mov_b32 v74, s17
	ml_addc_i32 v71, v74, v71, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v70, v[70:71], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v86, v70, 0xffff0000
	ml_shl_b32 v88, v70, 0x10
BB0_18:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0x40
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[22:23], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v70, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v71, v70, 0x1f
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v89, 0x0
	ml_mov_b32 v87, 0x0
	sl_cbr_wcrz BB0_20, wcr
; %bb.19:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v74, v70, 0x1
	ml_shl_b32 v71, v71, 0x1
	ml_addo_u32 {v74, tcr}, s16, v74
	ml_srl_b32 v75, v70, 0x1f
	ml_or_b32 v71, v71, v75
	ml_mov_b32 v75, s17
	ml_addc_i32 v75, v75, v71, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v71, v[74:75], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v87, v71, 0xffff0000
	ml_shl_b32 v89, v71, 0x10
BB0_20:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0x48
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[32:33], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v75, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v71, v75, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v94, 0x0
	ml_mov_b32 v92, 0x0
	sl_cbr_wcrz BB0_22, wcr
; %bb.21:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v74, v75, 0x1
	ml_shl_b32 v71, v71, 0x1
	ml_addo_u32 {v76, tcr}, s16, v74
	ml_srl_b32 v74, v75, 0x1f
	ml_or_b32 v71, v71, v74
	ml_mov_b32 v74, s17
	ml_addc_i32 v77, v74, v71, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v71, v[76:77], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v92, v71, 0xffff0000
	ml_shl_b32 v94, v71, 0x10
BB0_22:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0x50
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[24:25], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v71, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v74, v71, 0x1f
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v95, 0x0
	ml_mov_b32 v93, 0x0
	sl_cbr_wcrz BB0_24, wcr
; %bb.23:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v76, v71, 0x1
	ml_shl_b32 v74, v74, 0x1
	ml_addo_u32 {v76, tcr}, s16, v76
	ml_srl_b32 v77, v71, 0x1f
	ml_or_b32 v74, v74, v77
	ml_mov_b32 v77, s17
	ml_addc_i32 v77, v77, v74, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v74, v[76:77], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v93, v74, 0xffff0000
	ml_shl_b32 v95, v74, 0x10
BB0_24:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0x58
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[36:37], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v77, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v74, v77, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v100, 0x0
	ml_mov_b32 v98, 0x0
	sl_cbr_wcrz BB0_26, wcr
; %bb.25:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v76, v77, 0x1
	ml_shl_b32 v74, v74, 0x1
	ml_addo_u32 {v78, tcr}, s16, v76
	ml_srl_b32 v76, v77, 0x1f
	ml_or_b32 v74, v74, v76
	ml_mov_b32 v76, s17
	ml_addc_i32 v79, v76, v74, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v74, v[78:79], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v98, v74, 0xffff0000
	ml_shl_b32 v100, v74, 0x10
BB0_26:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0x60
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[30:31], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v74, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v76, v74, 0x1f
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v101, 0x0
	ml_mov_b32 v99, 0x0
	sl_cbr_wcrz BB0_28, wcr
; %bb.27:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v78, v74, 0x1
	ml_shl_b32 v76, v76, 0x1
	ml_addo_u32 {v78, tcr}, s16, v78
	ml_srl_b32 v79, v74, 0x1f
	ml_or_b32 v76, v76, v79
	ml_mov_b32 v79, s17
	ml_addc_i32 v79, v79, v76, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v76, v[78:79], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v99, v76, 0xffff0000
	ml_shl_b32 v101, v76, 0x10
BB0_28:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0x68
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[40:41], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v79, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v76, v79, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v107, 0x0
	ml_mov_b32 v105, 0x0
	sl_cbr_wcrz BB0_30, wcr
; %bb.29:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v78, v79, 0x1
	ml_shl_b32 v76, v76, 0x1
	ml_addo_u32 {v80, tcr}, s16, v78
	ml_srl_b32 v78, v79, 0x1f
	ml_or_b32 v76, v76, v78
	ml_mov_b32 v78, s17
	ml_addc_i32 v81, v78, v76, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v76, v[80:81], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v105, v76, 0xffff0000
	ml_shl_b32 v107, v76, 0x10
BB0_30:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0x70
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[34:35], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v76, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v78, v76, 0x1f
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v108, 0x0
	ml_mov_b32 v106, 0x0
	sl_cbr_wcrz BB0_32, wcr
; %bb.31:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v80, v76, 0x1
	ml_shl_b32 v78, v78, 0x1
	ml_addo_u32 {v80, tcr}, s16, v80
	ml_srl_b32 v81, v76, 0x1f
	ml_or_b32 v78, v78, v81
	ml_mov_b32 v81, s17
	ml_addc_i32 v81, v81, v78, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v78, v[80:81], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v106, v78, 0xffff0000
	ml_shl_b32 v108, v78, 0x10
BB0_32:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0x78
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[46:47], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v83, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v78, v83, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v112, 0x0
	ml_mov_b32 v110, 0x0
	sl_cbr_wcrz BB0_34, wcr
; %bb.33:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v80, v83, 0x1
	ml_shl_b32 v78, v78, 0x1
	ml_addo_u32 {v80, tcr}, s16, v80
	ml_srl_b32 v81, v83, 0x1f
	ml_or_b32 v78, v78, v81
	ml_mov_b32 v81, s17
	ml_addc_i32 v81, v81, v78, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v78, v[80:81], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v110, v78, 0xffff0000
	ml_shl_b32 v112, v78, 0x10
BB0_34:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0x80
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[38:39], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v78, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v80, v78, 0x1f
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v113, 0x0
	ml_mov_b32 v111, 0x0
	sl_cbr_wcrz BB0_36, wcr
; %bb.35:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v81, v78, 0x1
	ml_shl_b32 v84, v80, 0x1
	ml_addo_u32 {v80, tcr}, s16, v81
	ml_srl_b32 v81, v78, 0x1f
	ml_or_b32 v81, v84, v81
	ml_mov_b32 v84, s17
	ml_addc_i32 v81, v84, v81, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v80, v[80:81], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v111, v80, 0xffff0000
	ml_shl_b32 v113, v80, 0x10
BB0_36:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0x88
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[50:51], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v90, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v80, v90, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v117, 0x0
	ml_mov_b32 v115, 0x0
	sl_cbr_wcrz BB0_38, wcr
; %bb.37:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v81, v90, 0x1
	ml_shl_b32 v84, v80, 0x1
	ml_addo_u32 {v80, tcr}, s16, v81
	ml_srl_b32 v81, v90, 0x1f
	ml_or_b32 v81, v84, v81
	ml_mov_b32 v84, s17
	ml_addc_i32 v81, v84, v81, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v80, v[80:81], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v115, v80, 0xffff0000
	ml_shl_b32 v117, v80, 0x10
BB0_38:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0x90
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[42:43], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v80, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v81, v80, 0x1f
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v118, 0x0
	ml_mov_b32 v116, 0x0
	sl_cbr_wcrz BB0_40, wcr
; %bb.39:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v84, v80, 0x1
	ml_shl_b32 v81, v81, 0x1
	ml_addo_u32 {v96, tcr}, s16, v84
	ml_srl_b32 v84, v80, 0x1f
	ml_or_b32 v81, v81, v84
	ml_mov_b32 v84, s17
	ml_addc_i32 v97, v84, v81, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v81, v[96:97], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v116, v81, 0xffff0000
	ml_shl_b32 v118, v81, 0x10
BB0_40:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0x98
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[54:55], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v96, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v81, v96, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v122, 0x0
	ml_mov_b32 v120, 0x0
	sl_cbr_wcrz BB0_42, wcr
; %bb.41:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v84, v96, 0x1
	ml_shl_b32 v81, v81, 0x1
	ml_addo_u32 {v102, tcr}, s16, v84
	ml_srl_b32 v84, v96, 0x1f
	ml_or_b32 v81, v81, v84
	ml_mov_b32 v84, s17
	ml_addc_i32 v103, v84, v81, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v81, v[102:103], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v120, v81, 0xffff0000
	ml_shl_b32 v122, v81, 0x10
BB0_42:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0xa0
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[48:49], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v84, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v81, v84, 0x1f
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v123, 0x0
	ml_mov_b32 v121, 0x0
	sl_cbr_wcrz BB0_44, wcr
; %bb.43:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v91, v84, 0x1
	ml_shl_b32 v81, v81, 0x1
	ml_addo_u32 {v102, tcr}, s16, v91
	ml_srl_b32 v91, v84, 0x1f
	ml_or_b32 v81, v81, v91
	ml_mov_b32 v91, s17
	ml_addc_i32 v103, v91, v81, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v81, v[102:103], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v121, v81, 0xffff0000
	ml_shl_b32 v123, v81, 0x10
BB0_44:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0xa8
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[60:61], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v102, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v81, v102, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v127, 0x0
	ml_mov_b32 v125, 0x0
	sl_cbr_wcrz BB0_46, wcr
; %bb.45:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v91, v102, 0x1
	ml_shl_b32 v81, v81, 0x1
	ml_addo_u32 {v103, tcr}, s16, v91
	ml_srl_b32 v91, v102, 0x1f
	ml_or_b32 v81, v81, v91
	ml_mov_b32 v91, s17
	ml_addc_i32 v104, v91, v81, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v81, v[103:104], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v125, v81, 0xffff0000
	ml_shl_b32 v127, v81, 0x10
BB0_46:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0xb0
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[52:53], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v91, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v81, v91, 0x1f
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v128, 0x0
	ml_mov_b32 v126, 0x0
	sl_cbr_wcrz BB0_48, wcr
; %bb.47:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v97, v91, 0x1
	ml_shl_b32 v81, v81, 0x1
	ml_addo_u32 {v103, tcr}, s16, v97
	ml_srl_b32 v97, v91, 0x1f
	ml_or_b32 v81, v81, v97
	ml_mov_b32 v97, s17
	ml_addc_i32 v104, v97, v81, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v81, v[103:104], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v126, v81, 0xffff0000
	ml_shl_b32 v128, v81, 0x10
BB0_48:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0xb8
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[64:65], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v109, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v81, v109, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v131, 0x0
	ml_mov_b32 v129, 0x0
	sl_cbr_wcrz BB0_50, wcr
; %bb.49:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v97, v109, 0x1
	ml_shl_b32 v81, v81, 0x1
	ml_addo_u32 {v103, tcr}, s16, v97
	ml_srl_b32 v97, v109, 0x1f
	ml_or_b32 v81, v81, v97
	ml_mov_b32 v97, s17
	ml_addc_i32 v104, v97, v81, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v81, v[103:104], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v129, v81, 0xffff0000
	ml_shl_b32 v131, v81, 0x10
BB0_50:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0xc0
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[56:57], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v97, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v81, v97, 0x1f
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v132, 0x0
	ml_mov_b32 v130, 0x0
	sl_cbr_wcrz BB0_52, wcr
; %bb.51:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v103, v97, 0x1
	ml_shl_b32 v81, v81, 0x1
	ml_addo_u32 {v103, tcr}, s16, v103
	ml_srl_b32 v104, v97, 0x1f
	ml_or_b32 v81, v81, v104
	ml_mov_b32 v104, s17
	ml_addc_i32 v104, v104, v81, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v81, v[103:104], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v130, v81, 0xffff0000
	ml_shl_b32 v132, v81, 0x10
BB0_52:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0xc8
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[66:67], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v114, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v81, v114, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v135, 0x0
	ml_mov_b32 v133, 0x0
	sl_cbr_wcrz BB0_54, wcr
; %bb.53:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v103, v114, 0x1
	ml_shl_b32 v81, v81, 0x1
	ml_addo_u32 {v103, tcr}, s16, v103
	ml_srl_b32 v104, v114, 0x1f
	ml_or_b32 v81, v81, v104
	ml_mov_b32 v104, s17
	ml_addc_i32 v104, v104, v81, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v81, v[103:104], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v133, v81, 0xffff0000
	ml_shl_b32 v135, v81, 0x10
BB0_54:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0xd0
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[62:63], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v103, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v81, v103, 0x1f
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v136, 0x0
	ml_mov_b32 v134, 0x0
	sl_cbr_wcrz BB0_56, wcr
; %bb.55:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v104, v103, 0x1
	ml_shl_b32 v81, v81, 0x1
	ml_addo_u32 {v136, tcr}, s16, v104
	ml_srl_b32 v104, v103, 0x1f
	ml_or_b32 v81, v81, v104
	ml_mov_b32 v104, s17
	ml_addc_i32 v137, v104, v81, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v81, v[136:137], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v134, v81, 0xffff0000
	ml_shl_b32 v136, v81, 0x10
BB0_56:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0xd8
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[68:69], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v119, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v81, v119, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v139, 0x0
	ml_mov_b32 v137, 0x0
	sl_cbr_wcrz BB0_58, wcr
; %bb.57:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v104, v119, 0x1
	ml_shl_b32 v81, v81, 0x1
	ml_addo_u32 {v137, tcr}, s16, v104
	ml_srl_b32 v104, v119, 0x1f
	ml_or_b32 v81, v81, v104
	ml_mov_b32 v104, s17
	ml_addc_i32 v138, v104, v81, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v81, v[137:138], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v137, v81, 0xffff0000
	ml_shl_b32 v139, v81, 0x10
BB0_58:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0xe0
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[44:45], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v81, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v104, v81, 0x1f
	sl_mov_b32 s1, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v140, 0x0
	ml_mov_b32 v138, 0x0
	sl_cbr_wcrz BB0_60, wcr
; %bb.59:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v124, v81, 0x1
	ml_shl_b32 v104, v104, 0x1
	ml_addo_u32 {v140, tcr}, s16, v124
	ml_srl_b32 v124, v81, 0x1f
	ml_or_b32 v104, v104, v124
	ml_mov_b32 v124, s17
	ml_addc_i32 v141, v124, v104, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v104, v[140:141], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v138, v104, 0xffff0000
	ml_shl_b32 v140, v104, 0x10
BB0_60:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s2, s0, 0xe8
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s2, 0x7ee
	sl_sub_bi_u64 s[58:59], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s2, s2, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v104, s2, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v124, v104, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v142, 0x0
	ml_mov_b32 v141, 0x0
	sl_cbr_wcrz BB0_62, wcr
; %bb.61:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v141, v104, 0x1
	ml_shl_b32 v124, v124, 0x1
	ml_addo_u32 {v141, tcr}, s16, v141
	ml_srl_b32 v142, v104, 0x1f
	ml_or_b32 v124, v124, v142
	ml_mov_b32 v142, s17
	ml_addc_i32 v142, v142, v124, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v124, v[141:142], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v141, v124, 0xffff0000
	ml_shl_b32 v142, v124, 0x10
BB0_62:
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s1, s0, 0xf0
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s1, 0x7ee
	sl_sub_bi_u64 s[70:71], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s1, s1, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v124, s1, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v146, v124, 0x1f
	sl_mov_b32 s2, 0x0
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v144, 0x0
	ml_mov_b32 v143, 0x0
	sl_cbr_wcrz BB0_64, wcr
; %bb.63:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v143, v124, 0x1
	ml_shl_b32 v144, v146, 0x1
	ml_addo_u32 {v143, tcr}, s16, v143
	ml_srl_b32 v146, v124, 0x1f
	ml_or_b32 v144, v144, v146
	ml_mov_b32 v146, s17
	ml_addc_i32 v144, v146, v144, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v144, v[143:144], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v143, v144, 0xffff0000
	ml_shl_b32 v144, v144, 0x10
BB0_64:
	.loc	1 0 0                           ; candidate.py:0
	sl_and_b32 {s1, wcr}, s74, 0x380
	.loc	1 20 19 is_stmt 1               ; candidate.py:20:19
	sl_add_i32 s0, s0, 0xf8
	.loc	1 38 25                         ; candidate.py:38:25
	sl_cmp_lt_i32 wcr, s0, 0x7ee
	sl_sub_bi_u64 s[72:73], s[8:9], s[8:9], wcr
	.loc	1 39 25                         ; candidate.py:39:25
	sl_mull_u32 s0, s0, 0x1800
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v145, s0, v145
	.loc	1 42 30 is_stmt 1               ; candidate.py:42:30
	ml_sra_b32 v165, v145, 0x1f
	.loc	1 42 36 is_stmt 0               ; candidate.py:42:36
	ml_mov_b32 v147, 0x0
	ml_mov_b32 v146, 0x0
	sl_cbr_wcrz BB0_66, wcr
; %bb.65:
	.loc	1 42 30                         ; candidate.py:42:30
	ml_shl_b32 v146, v145, 0x1
	ml_shl_b32 v147, v165, 0x1
	ml_addo_u32 {v146, tcr}, s16, v146
	ml_srl_b32 v165, v145, 0x1f
	ml_or_b32 v147, v147, v165
	ml_mov_b32 v165, s17
	ml_addc_i32 v147, v165, v147, tcr
	.loc	1 42 36                         ; candidate.py:42:36
	ml_lsa_load_a64_dword  v147, v[146:147], kop=0
	.loc	1 42 54                         ; candidate.py:42:54
	sl_wait vmcnt(0)
	ml_and_b32 v146, v147, 0xffff0000
	ml_shl_b32 v147, v147, 0x10
BB0_66:
	.loc	1 37 23 is_stmt 1               ; candidate.py:37:23
	ml_cvt_bf16_f32  v62, v62
	ml_cvt_bf16_f32  v60, v60
	ml_cvt_bf16_f32  v58, v58
	ml_cvt_bf16_f32  v56, v56
	ml_cvt_bf16_f32  v54, v54
	ml_cvt_bf16_f32  v52, v52
	.loc	1 49 35                         ; candidate.py:49:35
	ml_mov_v2s_b32 s0, v150, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v42, v42
	ml_cvt_bf16_f32  v40, v40
	.loc	1 49 35                         ; candidate.py:49:35
	ml_shl_b32 v150, v148, 0x3
	sl_and_b32 {s0, wcr}, s0, 0xc00
	ml_shl_b32 v165, v148, 0xf
	sl_mull_u32 s2, s74, 0x400
	sl_and_b32 {s3, wcr}, s2, 0x10000
	sl_mull_u32 s2, s74, 0x20
	sl_and_b32 {s16, wcr}, s2, 0x1000
	sl_mov_b32 s2, 0x1000504
	sl_mov_b32 s17, 0x81f0
	ml_anyop3_b32 v150, v150, v165, s17, 0xffffffe0
	ml_byte_permute_b32 v168, v62, v60, s2
	ml_byte_permute_b32 v167, v58, v56, s2
	ml_byte_permute_b32 v166, v54, v52, s2
	ml_byte_permute_b32 v165, v42, v40, s2
	sl_add_i32 s0, s0, s16
	sl_add_i32 s0, s0, s3
	ml_slb_store_b32x4  v[165:168], v150, s0, #0, null
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v40, v63
	ml_cvt_bf16_f32  v42, v61
	ml_cvt_bf16_f32  v50, v50
	ml_cvt_bf16_f32  v52, v59
	ml_cvt_bf16_f32  v54, v57
	ml_cvt_bf16_f32  v48, v48
	ml_cvt_bf16_f32  v46, v46
	ml_cvt_bf16_f32  v55, v55
	ml_cvt_bf16_f32  v53, v53
	ml_cvt_bf16_f32  v44, v44
	ml_cvt_bf16_f32  v38, v38
	ml_cvt_bf16_f32  v56, v43
	ml_cvt_bf16_f32  v57, v41
	ml_cvt_bf16_f32  v36, v36
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v43, v40, v42, s2
	ml_byte_permute_b32 v42, v52, v54, s2
	ml_byte_permute_b32 v41, v55, v53, s2
	ml_byte_permute_b32 v40, v56, v57, s2
	ml_slb_store_b32x4  v[40:43], v150, s0, #512, null
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v30, v30
	ml_cvt_bf16_f32  v28, v28
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v43, v50, v48, s2
	ml_byte_permute_b32 v42, v46, v44, s2
	ml_byte_permute_b32 v41, v38, v36, s2
	ml_byte_permute_b32 v40, v30, v28, s2
	sl_add_i32 s3, s0, 0x2000
	ml_slb_store_b32x4  v[40:43], v150, s3, #0, null
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v28, v51
	ml_cvt_bf16_f32  v30, v49
	ml_cvt_bf16_f32  v34, v34
	ml_cvt_bf16_f32  v36, v47
	ml_cvt_bf16_f32  v38, v45
	ml_cvt_bf16_f32  v32, v32
	ml_cvt_bf16_f32  v26, v26
	ml_cvt_bf16_f32  v39, v39
	ml_cvt_bf16_f32  v37, v37
	ml_cvt_bf16_f32  v24, v24
	ml_cvt_bf16_f32  v22, v22
	ml_cvt_bf16_f32  v40, v31
	ml_cvt_bf16_f32  v41, v29
	ml_cvt_bf16_f32  v20, v20
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v31, v28, v30, s2
	ml_byte_permute_b32 v30, v36, v38, s2
	ml_byte_permute_b32 v29, v39, v37, s2
	ml_byte_permute_b32 v28, v40, v41, s2
	ml_slb_store_b32x4  v[28:31], v150, s3, #512, null
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v14, v14
	ml_cvt_bf16_f32  v12, v12
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v31, v34, v32, s2
	ml_byte_permute_b32 v30, v26, v24, s2
	ml_byte_permute_b32 v29, v22, v20, s2
	ml_byte_permute_b32 v28, v14, v12, s2
	sl_add_i32 s3, s0, 0x4000
	ml_slb_store_b32x4  v[28:31], v150, s3, #0, null
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v12, v35
	ml_cvt_bf16_f32  v14, v33
	ml_cvt_bf16_f32  v18, v18
	ml_cvt_bf16_f32  v20, v27
	ml_cvt_bf16_f32  v22, v25
	ml_cvt_bf16_f32  v16, v16
	ml_cvt_bf16_f32  v10, v10
	ml_cvt_bf16_f32  v23, v23
	ml_cvt_bf16_f32  v21, v21
	ml_cvt_bf16_f32  v8, v8
	ml_cvt_bf16_f32  v6, v6
	ml_cvt_bf16_f32  v24, v15
	ml_cvt_bf16_f32  v25, v13
	ml_cvt_bf16_f32  v4, v4
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v15, v12, v14, s2
	ml_byte_permute_b32 v14, v20, v22, s2
	ml_byte_permute_b32 v13, v23, v21, s2
	ml_byte_permute_b32 v12, v24, v25, s2
	ml_slb_store_b32x4  v[12:15], v150, s3, #512, null
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v2, v2
	ml_cvt_bf16_f32  v0, v0
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v15, v18, v16, s2
	ml_byte_permute_b32 v14, v10, v8, s2
	ml_byte_permute_b32 v13, v6, v4, s2
	ml_byte_permute_b32 v12, v2, v0, s2
	sl_add_i32 s0, s0, 0x6000
	ml_slb_store_b32x4  v[12:15], v150, s0, #0, null
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v0, v19
	ml_cvt_bf16_f32  v2, v17
	ml_cvt_bf16_f32  v4, v11
	ml_cvt_bf16_f32  v6, v9
	ml_cvt_bf16_f32  v7, v7
	ml_cvt_bf16_f32  v5, v5
	ml_cvt_bf16_f32  v8, v3
	ml_cvt_bf16_f32  v9, v1
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v3, v0, v2, s2
	ml_byte_permute_b32 v2, v4, v6, s2
	ml_byte_permute_b32 v1, v7, v5, s2
	ml_byte_permute_b32 v0, v8, v9, s2
	ml_slb_store_b32x4  v[0:3], v150, s0, #512, null
	sl_wait lmcnt(0)
	sl_barrier 
	ml_shl_b32 v0, v148, 0x8
	ml_and_b32 v0, v0, 0x7000
	ml_shl_b32 v1, v148, 0xd
	ml_or_b32 v1, v1, v149
	sl_mov_b32 s0, 0x10070
	ml_anyop3_b32 v29, s0, v1, v0, 0xfffffff8
	.loc	1 43 28                         ; candidate.py:43:28
	ml_slb_load_b32x4  v[24:27], v29, s1, #0, null
	.loc	1 49 35                         ; candidate.py:49:35
	sl_add_i32 s16, s1, 0x8000
	sl_add_i32 s74, s1, 0x400
	sl_add_i32 s75, s1, 0x8400
	.loc	1 43 28                         ; candidate.py:43:28
	ml_slb_load_b32x4  v[20:23], v29, s16, #0, null
	.loc	1 49 35                         ; candidate.py:49:35
	sl_add_i32 s0, s1, 0x800
	sl_add_i32 s3, s1, 0x8800
	sl_add_i32 s17, s1, 0x8c00
	.loc	1 43 28                         ; candidate.py:43:28
	ml_slb_load_b32x4  v[12:15], v29, s74, #0, null
	.loc	1 49 23                         ; candidate.py:49:23
	ml_addo_u32 {v30, tcr}, s18, v164
	ml_mov_b32 v2, s19
.Ltmp1:
	.file	2 "/usr/local/lib/python3.12/site-packages/triton/language" "standard.py"
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v3, 0, v161
.Ltmp2:
	.loc	1 43 28                         ; candidate.py:43:28
	ml_slb_load_b32x1  v0, v29, s16, #0, null
	.loc	1 49 35                         ; candidate.py:49:35
	sl_add_i32 s16, s1, 0xc00
.Ltmp3:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v3, v3, 0x3fb8aa3b
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v4, 0, v162
.Ltmp4:
	.loc	1 43 28 is_stmt 1               ; candidate.py:43:28
	ml_slb_load_b32x1  v1, v29, s1, #0, null
.Ltmp5:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v3, v3
	ml_mul_f32 v4, v4, 0x3fb8aa3b
.Ltmp6:
	.loc	1 49 23                         ; candidate.py:49:23
	ml_addc_i32 v31, v2, v163, tcr
	.loc	1 43 28                         ; candidate.py:43:28
	ml_slb_load_b32x4  v[16:19], v29, s75, #0, null
.Ltmp7:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v28, v4
.Ltmp8:
	.loc	1 43 28                         ; candidate.py:43:28
	sl_wait lmcnt(5)
	ml_and_b32 v24, v24, 0xffff0000
.Ltmp9:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v32, v3, 0x3f800000
.Ltmp10:
	.loc	1 43 28                         ; candidate.py:43:28
	ml_slb_load_b32x4  v[8:11], v29, s0, #0, null
.Ltmp11:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v33, v32
.Ltmp12:
	.loc	1 43 28                         ; candidate.py:43:28
	sl_wait lmcnt(5)
	ml_and_b32 v20, v20, 0xffff0000
.Ltmp13:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v36, v28, 0x3f800000
.Ltmp14:
	.loc	1 43 28                         ; candidate.py:43:28
	ml_slb_load_b32x4  v[4:7], v29, s3, #0, null
.Ltmp15:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v28, v32, 0x80000000
	ml_rcp_f32 v32, v36
	ml_fma_f32 v28, v28, v33, 1.0
.Ltmp16:
	.loc	1 43 28                         ; candidate.py:43:28
	sl_wait lmcnt(4)
	ml_shl_b32 v35, v0, 0x10
.Ltmp17:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_fma_f32 v37, v28, v33, v33
	ml_mov_b32 v28, 0x99
	ml_cmp_class_f32 tcr, v33, v28
.Ltmp18:
	.loc	1 43 28                         ; candidate.py:43:28
	sl_wait lmcnt(3)
	ml_shl_b32 v34, v1, 0x10
	ml_slb_load_b32x4  v[0:3], v29, s16, #0, null
.Ltmp19:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_csel_b32 v33, v33, v37, tcr
	ml_xor_b32 v36, v36, 0x80000000
	ml_fma_f32 v36, v36, v32, 1.0
	ml_fma_f32 v36, v36, v32, v32
	ml_cmp_class_f32 tcr, v32, v28
	ml_csel_b32 v32, v32, v36, tcr
.Ltmp20:
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v32, v32, v162
	ml_mul_f32 v33, v33, v161
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v33, v33, v35
.Ltmp21:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v35, 0, v159
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v35, v35, 0x3fb8aa3b
.Ltmp22:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v32, v32, v34
.Ltmp23:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v34, v35
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v35, 0, v160
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v35, v35, 0x3fb8aa3b
.Ltmp24:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v32, v32
.Ltmp25:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v35, v35
.Ltmp26:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v33, v33
.Ltmp27:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v34, v34, 0x3f800000
.Ltmp28:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v32, v33, v32, s2
.Ltmp29:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v33, v34
	ml_xor_b32 v34, v34, 0x80000000
	.loc	2 72 20 is_stmt 0               ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v35, v35, 0x3f800000
.Ltmp30:
	.loc	1 43 28 is_stmt 1               ; candidate.py:43:28
	ml_and_b32 v12, v12, 0xffff0000
.Ltmp31:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v36, v35
.Ltmp32:
	.loc	1 43 28                         ; candidate.py:43:28
	sl_wait lmcnt(3)
	ml_and_b32 v16, v16, 0xffff0000
.Ltmp33:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_fma_f32 v34, v34, v33, 1.0
	ml_fma_f32 v34, v34, v33, v33
	ml_cmp_class_f32 tcr, v33, v28
	ml_csel_b32 v33, v33, v34, tcr
	ml_xor_b32 v34, v35, 0x80000000
	ml_fma_f32 v34, v34, v36, 1.0
	ml_fma_f32 v34, v34, v36, v36
	ml_cmp_class_f32 tcr, v36, v28
	ml_csel_b32 v34, v36, v34, tcr
.Ltmp34:
	.loc	1 43 28                         ; candidate.py:43:28
	ml_slb_load_b32x1  v35, v29, s75, #0, null
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v34, v34, v160
	ml_mul_f32 v33, v33, v159
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v20, v33, v20
	.loc	1 43 28                         ; candidate.py:43:28
	ml_slb_load_b32x1  v33, v29, s74, #0, null
.Ltmp35:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v36, 0, v157
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v36, v36, 0x3fb8aa3b
.Ltmp36:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v24, v34, v24
.Ltmp37:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v34, v36
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v36, 0, v158
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v36, v36, 0x3fb8aa3b
.Ltmp38:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v24, v24
.Ltmp39:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v36, v36
.Ltmp40:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v20, v20
.Ltmp41:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v34, v34, 0x3f800000
.Ltmp42:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v20, v20, v24, s2
.Ltmp43:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v24, v34
	ml_xor_b32 v34, v34, 0x80000000
	.loc	2 72 20 is_stmt 0               ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v36, v36, 0x3f800000
.Ltmp44:
	.loc	1 43 28 is_stmt 1               ; candidate.py:43:28
	sl_wait lmcnt(4)
	ml_and_b32 v44, v8, 0xffff0000
	sl_wait lmcnt(1)
	ml_shl_b32 v35, v35, 0x10
.Ltmp45:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v37, v36
	ml_fma_f32 v34, v34, v24, 1.0
	ml_fma_f32 v34, v34, v24, v24
.Ltmp46:
	.loc	1 43 28                         ; candidate.py:43:28
	sl_wait lmcnt(0)
	ml_shl_b32 v33, v33, 0x10
.Ltmp47:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_cmp_class_f32 tcr, v24, v28
	ml_csel_b32 v24, v24, v34, tcr
	ml_xor_b32 v34, v36, 0x80000000
	ml_fma_f32 v34, v34, v37, 1.0
	ml_fma_f32 v34, v34, v37, v37
	ml_cmp_class_f32 tcr, v37, v28
	ml_csel_b32 v34, v37, v34, tcr
.Ltmp48:
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v34, v34, v158
	ml_mul_f32 v24, v24, v157
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v24, v24, v35
.Ltmp49:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v35, 0, v155
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v35, v35, 0x3fb8aa3b
.Ltmp50:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v33, v34, v33
.Ltmp51:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v34, v35
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v35, 0, v156
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v35, v35, 0x3fb8aa3b
.Ltmp52:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v33, v33
.Ltmp53:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v35, v35
.Ltmp54:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v24, v24
.Ltmp55:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v34, v34, 0x3f800000
.Ltmp56:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v24, v24, v33, s2
.Ltmp57:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v33, v34
	ml_xor_b32 v34, v34, 0x80000000
	.loc	2 72 20 is_stmt 0               ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v35, v35, 0x3f800000
.Ltmp58:
	.loc	1 43 28 is_stmt 1               ; candidate.py:43:28
	ml_and_b32 v45, v4, 0xffff0000
.Ltmp59:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v36, v35
.Ltmp60:
	.loc	1 43 28                         ; candidate.py:43:28
	ml_shl_b32 v38, v25, 0x10
.Ltmp61:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_fma_f32 v34, v34, v33, 1.0
	ml_fma_f32 v34, v34, v33, v33
	ml_cmp_class_f32 tcr, v33, v28
	ml_csel_b32 v33, v33, v34, tcr
	ml_xor_b32 v34, v35, 0x80000000
	ml_fma_f32 v34, v34, v36, 1.0
	ml_fma_f32 v34, v34, v36, v36
	ml_cmp_class_f32 tcr, v36, v28
	ml_csel_b32 v34, v36, v34, tcr
.Ltmp62:
	.loc	1 43 28                         ; candidate.py:43:28
	ml_slb_load_b32x1  v35, v29, s3, #0, null
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v34, v34, v156
	ml_mul_f32 v33, v33, v155
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v16, v33, v16
	.loc	1 43 28                         ; candidate.py:43:28
	ml_slb_load_b32x1  v36, v29, s0, #0, null
.Ltmp63:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v33, 0, v153
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v33, v33, 0x3fb8aa3b
.Ltmp64:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v12, v34, v12
.Ltmp65:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v33, v33
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v34, 0, v154
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v34, v34, 0x3fb8aa3b
.Ltmp66:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v12, v12
.Ltmp67:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v34, v34
.Ltmp68:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v16, v16
.Ltmp69:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v37, v33, 0x3f800000
.Ltmp70:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v33, v16, v12, s2
.Ltmp71:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v12, v37
.Ltmp72:
	.loc	1 43 28                         ; candidate.py:43:28
	ml_shl_b32 v40, v21, 0x10
.Ltmp73:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v34, v34, 0x3f800000
.Ltmp74:
	.loc	1 43 28                         ; candidate.py:43:28
	ml_and_b32 v41, v25, 0xffff0000
	sl_wait lmcnt(1)
	ml_shl_b32 v35, v35, 0x10
	ml_and_b32 v42, v21, 0xffff0000
.Ltmp75:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_cmp_class_f32 tcr, v12, v28
.Ltmp76:
	.loc	1 43 28                         ; candidate.py:43:28
	ml_and_b32 v39, v17, 0xffff0000
	sl_wait lmcnt(0)
	ml_shl_b32 v16, v36, 0x10
.Ltmp77:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v36, v37, 0x80000000
	ml_rcp_f32 v37, v34
	ml_fma_f32 v36, v36, v12, 1.0
	ml_fma_f32 v36, v36, v12, v12
	ml_csel_b32 v12, v12, v36, tcr
	ml_xor_b32 v34, v34, 0x80000000
.Ltmp78:
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v12, v12, v153
.Ltmp79:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_fma_f32 v34, v34, v37, 1.0
	ml_fma_f32 v34, v34, v37, v37
	ml_cmp_class_f32 tcr, v37, v28
	ml_csel_b32 v34, v37, v34, tcr
.Ltmp80:
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v34, v34, v154
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v12, v12, v35
.Ltmp81:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v35, 0, v151
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v35, v35, 0x3fb8aa3b
.Ltmp82:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v16, v34, v16
.Ltmp83:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v34, v35
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v35, 0, v152
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v35, v35, 0x3fb8aa3b
.Ltmp84:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v16, v16
.Ltmp85:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v35, v35
.Ltmp86:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v12, v12
.Ltmp87:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v34, v34, 0x3f800000
.Ltmp88:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v43, v12, v16, s2
.Ltmp89:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v12, v34
	ml_xor_b32 v8, v34, 0x80000000
	.loc	2 72 20 is_stmt 0               ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v4, v35, 0x3f800000
.Ltmp90:
	.loc	1 43 28 is_stmt 1               ; candidate.py:43:28
	ml_shl_b32 v35, v13, 0x10
.Ltmp91:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v16, v4
	ml_xor_b32 v4, v4, 0x80000000
	ml_fma_f32 v8, v8, v12, 1.0
	ml_fma_f32 v8, v8, v12, v12
	ml_cmp_class_f32 tcr, v12, v28
	ml_csel_b32 v8, v12, v8, tcr
	ml_fma_f32 v4, v4, v16, 1.0
	ml_fma_f32 v4, v4, v16, v16
	ml_cmp_class_f32 tcr, v16, v28
	ml_csel_b32 v4, v16, v4, tcr
.Ltmp92:
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v46, v4, v152
	ml_mul_f32 v47, v8, v151
	.loc	1 43 28                         ; candidate.py:43:28
	ml_shl_b32 v36, v17, 0x10
	ml_and_b32 v37, v13, 0xffff0000
	ml_shl_b32 v25, v9, 0x10
	ml_and_b32 v34, v9, 0xffff0000
	ml_shl_b32 v17, v26, 0x10
	ml_and_b32 v21, v26, 0xffff0000
	ml_shl_b32 v9, v27, 0x10
	ml_and_b32 v13, v27, 0xffff0000
	ml_shl_b32 v50, v22, 0x10
	ml_and_b32 v48, v22, 0xffff0000
	ml_shl_b32 v22, v23, 0x10
	ml_and_b32 v16, v23, 0xffff0000
	ml_shl_b32 v26, v14, 0x10
	ml_and_b32 v23, v14, 0xffff0000
	ml_shl_b32 v8, v15, 0x10
	ml_and_b32 v12, v15, 0xffff0000
	ml_shl_b32 v49, v18, 0x10
	ml_and_b32 v27, v18, 0xffff0000
	ml_shl_b32 v15, v19, 0x10
	ml_and_b32 v14, v19, 0xffff0000
	ml_shl_b32 v19, v10, 0x10
	ml_and_b32 v18, v10, 0xffff0000
	ml_shl_b32 v4, v11, 0x10
	ml_and_b32 v10, v11, 0xffff0000
	ml_and_b32 v55, v0, 0xffff0000
	.loc	1 49 35                         ; candidate.py:49:35
	ml_mov_v2s_b32 s0, v30, 0x0
	.loc	1 43 28                         ; candidate.py:43:28
	ml_shl_b32 v56, v5, 0x10
	ml_and_b32 v57, v5, 0xffff0000
	.loc	1 49 35                         ; candidate.py:49:35
	ml_mov_v2s_b32 s1, v31, 0x0
	ml_mov_b32 v0, s0
	ml_sub_i32 v0, v30, v0
	sl_mov_b32 s3, 0xffffffff
	ml_sub_i32 v5, v65, v64
	ml_shl_b32 v5, v5, 0x1
	ml_mov_v2s_b32 s18, v5, 0x0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v32, s[0:3], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 28                         ; candidate.py:43:28
	ml_shl_b32 v58, v1, 0x10
	ml_and_b32 v59, v1, 0xffff0000
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v1, s18, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v20, s[0:3], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 28                         ; candidate.py:43:28
	ml_shl_b32 v32, v6, 0x10
	ml_and_b32 v30, v6, 0xffff0000
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v1, v66, v64
	ml_shl_b32 v1, v1, 0x1
	ml_mov_v2s_b32 s4, v1, 0x0
	.loc	1 43 28                         ; candidate.py:43:28
	ml_shl_b32 v11, v7, 0x10
	ml_and_b32 v6, v7, 0xffff0000
	ml_shl_b32 v20, v2, 0x10
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v1, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[10:11], tmsk
	ml_lsa_store_dword v24, s[0:3], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 28                         ; candidate.py:43:28
	ml_and_b32 v7, v2, 0xffff0000
	ml_shl_b32 v5, v3, 0x10
	ml_and_b32 v1, v3, 0xffff0000
	ml_slb_load_b32x4  v[51:54], v29, s17, #0, null
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v2, v47, v45
.Ltmp93:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v3, 0, v82
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v3, v3, 0x3fb8aa3b
.Ltmp94:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v24, v46, v44
.Ltmp95:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v3, v3
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v31, 0, v85
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v31, v31, 0x3fb8aa3b
.Ltmp96:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v24, v24
.Ltmp97:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v44, v31
.Ltmp98:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v2, v2
.Ltmp99:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v45, v3, 0x3f800000
.Ltmp100:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v2, v2, v24, s2
.Ltmp101:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v46, v45
.Ltmp102:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v3, v67, v64
	ml_shl_b32 v3, v3, 0x1
	ml_mov_v2s_b32 s4, v3, 0x0
	ml_sub_i32 v3, v68, v64
	ml_shl_b32 v3, v3, 0x1
	ml_mov_v2s_b32 s5, v3, 0x0
	.loc	1 43 28                         ; candidate.py:43:28
	sl_wait lmcnt(0)
	ml_and_b32 v47, v51, 0xffff0000
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v3, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[12:13], tmsk
	ml_lsa_store_dword v33, s[0:3], signed v3, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 28                         ; candidate.py:43:28
	ml_shl_b32 v33, v52, 0x10
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v3, s5, v0
	ml_sub_i32 v24, v72, v64
	ml_shl_b32 v24, v24, 0x1
	ml_mov_v2s_b32 s4, v24, 0x0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[14:15], tmsk
	ml_lsa_store_dword v43, s[0:3], signed v3, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 28                         ; candidate.py:43:28
	ml_and_b32 v43, v52, 0xffff0000
	ml_shl_b32 v31, v53, 0x10
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v3, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[26:27], tmsk
	ml_lsa_store_dword v2, s[0:3], signed v3, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 28                         ; candidate.py:43:28
	ml_and_b32 v24, v53, 0xffff0000
	ml_shl_b32 v3, v54, 0x10
	ml_and_b32 v2, v54, 0xffff0000
	ml_slb_load_b32x1  v51, v29, s17, #0, null
.Ltmp103:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v44, v44, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v45, v45, 0x80000000
	ml_fma_f32 v45, v45, v46, 1.0
	ml_rcp_f32 v52, v44
	ml_fma_f32 v45, v45, v46, v46
	ml_cmp_class_f32 tcr, v46, v28
	ml_csel_b32 v45, v46, v45, tcr
.Ltmp104:
	.loc	1 43 28 is_stmt 1               ; candidate.py:43:28
	ml_slb_load_b32x1  v29, v29, s16, #0, null
.Ltmp105:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v44, v44, 0x80000000
	ml_fma_f32 v44, v44, v52, 1.0
	ml_fma_f32 v44, v44, v52, v52
	ml_cmp_class_f32 tcr, v52, v28
	ml_csel_b32 v44, v52, v44, tcr
.Ltmp106:
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v44, v44, v85
	ml_mul_f32 v45, v45, v82
	.loc	1 43 28                         ; candidate.py:43:28
	sl_wait lmcnt(1)
	ml_shl_b32 v46, v51, 0x10
.Ltmp107:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v51, 0, v86
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v51, v51, 0x3fb8aa3b
.Ltmp108:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v45, v45, v46
.Ltmp109:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v46, v51
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v51, 0, v88
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v51, v51, 0x3fb8aa3b
.Ltmp110:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v45, v45
	.loc	1 43 28                         ; candidate.py:43:28
	sl_wait lmcnt(0)
	ml_shl_b32 v29, v29, 0x10
.Ltmp111:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v51, v51
.Ltmp112:
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v29, v44, v29
.Ltmp113:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v44, v46, 0x3f800000
.Ltmp114:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v29, v29
.Ltmp115:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v46, v44
.Ltmp116:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v29, v45, v29, s2
.Ltmp117:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v45, v51, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v44, v44, 0x80000000
	ml_rcp_f32 v51, v45
	ml_xor_b32 v45, v45, 0x80000000
	ml_fma_f32 v44, v44, v46, 1.0
	ml_fma_f32 v44, v44, v46, v46
	ml_cmp_class_f32 tcr, v46, v28
	ml_csel_b32 v44, v46, v44, tcr
	ml_fma_f32 v45, v45, v51, 1.0
	ml_fma_f32 v45, v45, v51, v51
	ml_cmp_class_f32 tcr, v51, v28
	ml_csel_b32 v45, v51, v45, tcr
.Ltmp118:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v45, v45, v88
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v46, v69, v64
	ml_shl_b32 v46, v46, 0x1
	ml_mov_v2s_b32 s4, v46, 0x0
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v44, v44, v86
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v44, v44, v47
	ml_mul_f32 v45, v45, v55
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v46, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[20:21], tmsk
	ml_lsa_store_dword v29, s[0:3], signed v46, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp119:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v29, 0, v87
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v29, v29, 0x3fb8aa3b
.Ltmp120:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v45, v45
.Ltmp121:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v29, v29
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v46, 0, v89
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v46, v46, 0x3fb8aa3b
.Ltmp122:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v44, v44
.Ltmp123:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v46, v46
.Ltmp124:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v47, v73, v64
	ml_shl_b32 v47, v47, 0x1
	ml_mov_v2s_b32 s4, v47, 0x0
.Ltmp125:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v29, v29, 0x3f800000
.Ltmp126:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v44, v44, v45, s2
.Ltmp127:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v45, v29
.Ltmp128:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v47, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[28:29], tmsk
	ml_lsa_store_dword v44, s[0:3], signed v47, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp129:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v44, v46, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v29, v29, 0x80000000
	ml_rcp_f32 v46, v44
	ml_fma_f32 v29, v29, v45, 1.0
	ml_fma_f32 v29, v29, v45, v45
	ml_cmp_class_f32 tcr, v45, v28
	ml_csel_b32 v29, v45, v29, tcr
	ml_xor_b32 v44, v44, 0x80000000
	ml_fma_f32 v44, v44, v46, 1.0
	ml_fma_f32 v44, v44, v46, v46
	ml_cmp_class_f32 tcr, v46, v28
	ml_csel_b32 v44, v46, v44, tcr
.Ltmp130:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v44, v44, v89
.Ltmp131:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v45, 0, v92
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v45, v45, 0x3fb8aa3b
.Ltmp132:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v29, v29, v87
.Ltmp133:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v45, v45
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v46, 0, v94
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v46, v46, 0x3fb8aa3b
.Ltmp134:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v29, v29, v40
.Ltmp135:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v40, v46
.Ltmp136:
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v38, v44, v38
.Ltmp137:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v44, v45, 0x3f800000
.Ltmp138:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v38, v38
.Ltmp139:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v45, v44
.Ltmp140:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v29, v29
	ml_byte_permute_b32 v29, v29, v38, s2
.Ltmp141:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v38, v40, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v40, v44, 0x80000000
	ml_rcp_f32 v44, v38
	ml_fma_f32 v40, v40, v45, 1.0
	ml_fma_f32 v40, v40, v45, v45
	ml_cmp_class_f32 tcr, v45, v28
	ml_csel_b32 v40, v45, v40, tcr
	ml_xor_b32 v38, v38, 0x80000000
	ml_fma_f32 v38, v38, v44, 1.0
	ml_fma_f32 v38, v38, v44, v44
	ml_cmp_class_f32 tcr, v44, v28
	ml_csel_b32 v38, v44, v38, tcr
.Ltmp142:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v38, v38, v94
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v44, v70, v64
	ml_shl_b32 v44, v44, 0x1
	ml_mov_v2s_b32 s4, v44, 0x0
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v40, v40, v92
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v40, v40, v42
	ml_mul_f32 v38, v38, v41
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v41, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v29, s[0:3], signed v41, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp143:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v29, 0, v93
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v29, v29, 0x3fb8aa3b
.Ltmp144:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v38, v38
.Ltmp145:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v29, v29
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v41, 0, v95
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v41, v41, 0x3fb8aa3b
.Ltmp146:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v40, v40
.Ltmp147:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v41, v41
.Ltmp148:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v42, v75, v64
	ml_shl_b32 v42, v42, 0x1
	ml_mov_v2s_b32 s4, v42, 0x0
.Ltmp149:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v29, v29, 0x3f800000
.Ltmp150:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v38, v40, v38, s2
.Ltmp151:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v40, v29
.Ltmp152:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v42, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[32:33], tmsk
	ml_lsa_store_dword v38, s[0:3], signed v42, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp153:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v38, v41, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v29, v29, 0x80000000
	ml_rcp_f32 v41, v38
	ml_fma_f32 v29, v29, v40, 1.0
	ml_fma_f32 v29, v29, v40, v40
	ml_cmp_class_f32 tcr, v40, v28
	ml_csel_b32 v29, v40, v29, tcr
	ml_xor_b32 v38, v38, 0x80000000
	ml_fma_f32 v38, v38, v41, 1.0
	ml_fma_f32 v38, v38, v41, v41
	ml_cmp_class_f32 tcr, v41, v28
	ml_csel_b32 v38, v41, v38, tcr
.Ltmp154:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v38, v38, v95
.Ltmp155:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v40, 0, v98
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v40, v40, 0x3fb8aa3b
.Ltmp156:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v29, v29, v93
.Ltmp157:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v40, v40
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v41, 0, v100
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v41, v41, 0x3fb8aa3b
.Ltmp158:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v29, v29, v36
.Ltmp159:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v36, v41
.Ltmp160:
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v35, v38, v35
.Ltmp161:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v38, v40, 0x3f800000
.Ltmp162:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v35, v35
.Ltmp163:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v40, v38
.Ltmp164:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v29, v29
	ml_byte_permute_b32 v29, v29, v35, s2
.Ltmp165:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v35, v36, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v36, v38, 0x80000000
	ml_rcp_f32 v38, v35
	ml_fma_f32 v36, v36, v40, 1.0
	ml_fma_f32 v36, v36, v40, v40
	ml_cmp_class_f32 tcr, v40, v28
	ml_csel_b32 v36, v40, v36, tcr
	ml_xor_b32 v35, v35, 0x80000000
	ml_fma_f32 v35, v35, v38, 1.0
	ml_fma_f32 v35, v35, v38, v38
	ml_cmp_class_f32 tcr, v38, v28
	ml_csel_b32 v35, v38, v35, tcr
.Ltmp166:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v35, v35, v100
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v38, v71, v64
	ml_shl_b32 v38, v38, 0x1
	ml_mov_v2s_b32 s4, v38, 0x0
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v36, v36, v98
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v36, v36, v39
	ml_mul_f32 v35, v35, v37
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v37, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v29, s[0:3], signed v37, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp167:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v29, 0, v99
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v29, v29, 0x3fb8aa3b
.Ltmp168:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v35, v35
.Ltmp169:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v29, v29
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v37, 0, v101
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v37, v37, 0x3fb8aa3b
.Ltmp170:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v36, v36
.Ltmp171:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v37, v37
.Ltmp172:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v38, v77, v64
	ml_shl_b32 v38, v38, 0x1
	ml_mov_v2s_b32 s4, v38, 0x0
.Ltmp173:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v29, v29, 0x3f800000
.Ltmp174:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v35, v36, v35, s2
.Ltmp175:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v36, v29
.Ltmp176:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v38, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[36:37], tmsk
	ml_lsa_store_dword v35, s[0:3], signed v38, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp177:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v35, v37, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v29, v29, 0x80000000
	ml_rcp_f32 v37, v35
	ml_fma_f32 v29, v29, v36, 1.0
	ml_fma_f32 v29, v29, v36, v36
	ml_cmp_class_f32 tcr, v36, v28
	ml_csel_b32 v29, v36, v29, tcr
	ml_xor_b32 v35, v35, 0x80000000
	ml_fma_f32 v35, v35, v37, 1.0
	ml_fma_f32 v35, v35, v37, v37
	ml_cmp_class_f32 tcr, v37, v28
	ml_csel_b32 v35, v37, v35, tcr
.Ltmp178:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v35, v35, v101
.Ltmp179:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v36, 0, v105
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v36, v36, 0x3fb8aa3b
.Ltmp180:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v29, v29, v99
.Ltmp181:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v36, v36
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v37, 0, v107
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v37, v37, 0x3fb8aa3b
.Ltmp182:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v29, v29, v56
.Ltmp183:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v37, v37
.Ltmp184:
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v25, v35, v25
.Ltmp185:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v35, v36, 0x3f800000
.Ltmp186:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v25, v25
.Ltmp187:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v36, v35
.Ltmp188:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v29, v29
	ml_byte_permute_b32 v25, v29, v25, s2
.Ltmp189:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v29, v37, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v35, v35, 0x80000000
	ml_rcp_f32 v37, v29
	ml_fma_f32 v35, v35, v36, 1.0
	ml_fma_f32 v35, v35, v36, v36
	ml_cmp_class_f32 tcr, v36, v28
	ml_csel_b32 v35, v36, v35, tcr
	ml_xor_b32 v29, v29, 0x80000000
	ml_fma_f32 v29, v29, v37, 1.0
	ml_fma_f32 v29, v29, v37, v37
	ml_cmp_class_f32 tcr, v37, v28
	ml_csel_b32 v29, v37, v29, tcr
.Ltmp190:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v29, v29, v107
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v36, v74, v64
	ml_shl_b32 v36, v36, 0x1
	ml_mov_v2s_b32 s4, v36, 0x0
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v35, v35, v105
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v35, v35, v57
	ml_mul_f32 v29, v29, v34
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v34, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[30:31], tmsk
	ml_lsa_store_dword v25, s[0:3], signed v34, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp191:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v25, 0, v106
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v25, v25, 0x3fb8aa3b
.Ltmp192:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v29, v29
.Ltmp193:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v25, v25
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v34, 0, v108
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v34, v34, 0x3fb8aa3b
.Ltmp194:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v35, v35
.Ltmp195:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v34, v34
.Ltmp196:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v36, v79, v64
	ml_shl_b32 v36, v36, 0x1
	ml_mov_v2s_b32 s4, v36, 0x0
.Ltmp197:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v25, v25, 0x3f800000
.Ltmp198:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v29, v35, v29, s2
.Ltmp199:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v35, v25
.Ltmp200:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v36, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[40:41], tmsk
	ml_lsa_store_dword v29, s[0:3], signed v36, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp201:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v29, v34, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v25, v25, 0x80000000
	ml_rcp_f32 v34, v29
	ml_fma_f32 v25, v25, v35, 1.0
	ml_fma_f32 v25, v25, v35, v35
	ml_cmp_class_f32 tcr, v35, v28
	ml_csel_b32 v25, v35, v25, tcr
	ml_xor_b32 v29, v29, 0x80000000
	ml_fma_f32 v29, v29, v34, 1.0
	ml_fma_f32 v29, v29, v34, v34
	ml_cmp_class_f32 tcr, v34, v28
	ml_csel_b32 v29, v34, v29, tcr
.Ltmp202:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v29, v29, v108
.Ltmp203:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v34, 0, v110
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v34, v34, 0x3fb8aa3b
.Ltmp204:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v25, v25, v106
.Ltmp205:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v34, v34
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v35, 0, v112
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v35, v35, 0x3fb8aa3b
.Ltmp206:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v25, v25, v33
.Ltmp207:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v33, v35
.Ltmp208:
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v29, v29, v58
.Ltmp209:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v34, v34, 0x3f800000
.Ltmp210:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v29, v29
.Ltmp211:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v35, v34
.Ltmp212:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v25, v25
	ml_byte_permute_b32 v25, v25, v29, s2
.Ltmp213:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v29, v33, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v33, v34, 0x80000000
	ml_rcp_f32 v34, v29
	ml_fma_f32 v33, v33, v35, 1.0
	ml_fma_f32 v33, v33, v35, v35
	ml_cmp_class_f32 tcr, v35, v28
	ml_csel_b32 v33, v35, v33, tcr
	ml_xor_b32 v29, v29, 0x80000000
	ml_fma_f32 v29, v29, v34, 1.0
	ml_fma_f32 v29, v29, v34, v34
	ml_cmp_class_f32 tcr, v34, v28
	ml_csel_b32 v29, v34, v29, tcr
.Ltmp214:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v29, v29, v112
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v34, v76, v64
	ml_shl_b32 v34, v34, 0x1
	ml_mov_v2s_b32 s4, v34, 0x0
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v33, v33, v110
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v33, v33, v43
	ml_mul_f32 v29, v29, v59
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v34, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[34:35], tmsk
	ml_lsa_store_dword v25, s[0:3], signed v34, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp215:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v25, 0, v111
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v25, v25, 0x3fb8aa3b
.Ltmp216:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v29, v29
.Ltmp217:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v25, v25
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v34, 0, v113
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v34, v34, 0x3fb8aa3b
.Ltmp218:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v33, v33
.Ltmp219:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v34, v34
.Ltmp220:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v35, v83, v64
	ml_shl_b32 v35, v35, 0x1
	ml_mov_v2s_b32 s4, v35, 0x0
.Ltmp221:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v25, v25, 0x3f800000
.Ltmp222:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v29, v33, v29, s2
.Ltmp223:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v33, v25
.Ltmp224:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v35, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[46:47], tmsk
	ml_lsa_store_dword v29, s[0:3], signed v35, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp225:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v29, v34, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v25, v25, 0x80000000
	ml_rcp_f32 v34, v29
	ml_fma_f32 v25, v25, v33, 1.0
	ml_fma_f32 v25, v25, v33, v33
	ml_cmp_class_f32 tcr, v33, v28
	ml_csel_b32 v25, v33, v25, tcr
	ml_xor_b32 v29, v29, 0x80000000
	ml_fma_f32 v29, v29, v34, 1.0
	ml_fma_f32 v29, v29, v34, v34
	ml_cmp_class_f32 tcr, v34, v28
	ml_csel_b32 v29, v34, v29, tcr
.Ltmp226:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v29, v29, v113
.Ltmp227:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v33, 0, v115
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v33, v33, 0x3fb8aa3b
.Ltmp228:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v25, v25, v111
.Ltmp229:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v33, v33
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v34, 0, v117
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v34, v34, 0x3fb8aa3b
.Ltmp230:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v25, v25, v50
.Ltmp231:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v34, v34
.Ltmp232:
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v17, v29, v17
.Ltmp233:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v29, v33, 0x3f800000
.Ltmp234:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v17, v17
.Ltmp235:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v33, v29
.Ltmp236:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v25, v25
	ml_byte_permute_b32 v17, v25, v17, s2
.Ltmp237:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v25, v34, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v29, v29, 0x80000000
	ml_rcp_f32 v34, v25
	ml_fma_f32 v29, v29, v33, 1.0
	ml_fma_f32 v29, v29, v33, v33
	ml_cmp_class_f32 tcr, v33, v28
	ml_csel_b32 v29, v33, v29, tcr
	ml_xor_b32 v25, v25, 0x80000000
	ml_fma_f32 v25, v25, v34, 1.0
	ml_fma_f32 v25, v25, v34, v34
	ml_cmp_class_f32 tcr, v34, v28
	ml_csel_b32 v25, v34, v25, tcr
.Ltmp238:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v25, v25, v117
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v33, v78, v64
	ml_shl_b32 v33, v33, 0x1
	ml_mov_v2s_b32 s4, v33, 0x0
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v29, v29, v115
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v29, v29, v48
	ml_mul_f32 v21, v25, v21
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v25, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[38:39], tmsk
	ml_lsa_store_dword v17, s[0:3], signed v25, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp239:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v17, 0, v116
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v17, v17, 0x3fb8aa3b
.Ltmp240:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v21, v21
.Ltmp241:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v17, v17
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v25, 0, v118
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v25, v25, 0x3fb8aa3b
.Ltmp242:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v29, v29
.Ltmp243:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v25, v25
.Ltmp244:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v33, v90, v64
	ml_shl_b32 v33, v33, 0x1
	ml_mov_v2s_b32 s4, v33, 0x0
.Ltmp245:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v17, v17, 0x3f800000
.Ltmp246:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v21, v29, v21, s2
.Ltmp247:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v29, v17
.Ltmp248:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v33, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[50:51], tmsk
	ml_lsa_store_dword v21, s[0:3], signed v33, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp249:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v21, v25, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v17, v17, 0x80000000
	ml_rcp_f32 v25, v21
	ml_fma_f32 v17, v17, v29, 1.0
	ml_fma_f32 v17, v17, v29, v29
	ml_cmp_class_f32 tcr, v29, v28
	ml_csel_b32 v17, v29, v17, tcr
	ml_xor_b32 v21, v21, 0x80000000
	ml_fma_f32 v21, v21, v25, 1.0
	ml_fma_f32 v21, v21, v25, v25
	ml_cmp_class_f32 tcr, v25, v28
	ml_csel_b32 v21, v25, v21, tcr
.Ltmp250:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v21, v21, v118
.Ltmp251:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v25, 0, v120
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v25, v25, 0x3fb8aa3b
.Ltmp252:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v17, v17, v116
.Ltmp253:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v25, v25
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v29, 0, v122
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v29, v29, 0x3fb8aa3b
.Ltmp254:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v17, v17, v49
.Ltmp255:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v29, v29
.Ltmp256:
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v21, v21, v26
.Ltmp257:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v25, v25, 0x3f800000
.Ltmp258:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v21, v21
.Ltmp259:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v26, v25
.Ltmp260:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v17, v17
	ml_byte_permute_b32 v17, v17, v21, s2
.Ltmp261:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v21, v29, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v25, v25, 0x80000000
	ml_rcp_f32 v29, v21
	ml_fma_f32 v25, v25, v26, 1.0
	ml_fma_f32 v25, v25, v26, v26
	ml_cmp_class_f32 tcr, v26, v28
	ml_csel_b32 v25, v26, v25, tcr
	ml_xor_b32 v21, v21, 0x80000000
	ml_fma_f32 v21, v21, v29, 1.0
	ml_fma_f32 v21, v21, v29, v29
	ml_cmp_class_f32 tcr, v29, v28
	ml_csel_b32 v21, v29, v21, tcr
.Ltmp262:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v21, v21, v122
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v26, v80, v64
	ml_shl_b32 v26, v26, 0x1
	ml_mov_v2s_b32 s4, v26, 0x0
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v25, v25, v120
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v25, v25, v27
	ml_mul_f32 v21, v21, v23
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v23, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[42:43], tmsk
	ml_lsa_store_dword v17, s[0:3], signed v23, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp263:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v17, 0, v121
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v17, v17, 0x3fb8aa3b
.Ltmp264:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v21, v21
.Ltmp265:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v17, v17
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v23, 0, v123
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v23, v23, 0x3fb8aa3b
.Ltmp266:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v25, v25
.Ltmp267:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v23, v23
.Ltmp268:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v26, v96, v64
	ml_shl_b32 v26, v26, 0x1
	ml_mov_v2s_b32 s4, v26, 0x0
.Ltmp269:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v17, v17, 0x3f800000
.Ltmp270:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v21, v25, v21, s2
.Ltmp271:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v25, v17
.Ltmp272:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v26, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[54:55], tmsk
	ml_lsa_store_dword v21, s[0:3], signed v26, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp273:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v21, v23, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v17, v17, 0x80000000
	ml_rcp_f32 v23, v21
	ml_fma_f32 v17, v17, v25, 1.0
	ml_fma_f32 v17, v17, v25, v25
	ml_cmp_class_f32 tcr, v25, v28
	ml_csel_b32 v17, v25, v17, tcr
	ml_xor_b32 v21, v21, 0x80000000
	ml_fma_f32 v21, v21, v23, 1.0
	ml_fma_f32 v21, v21, v23, v23
	ml_cmp_class_f32 tcr, v23, v28
	ml_csel_b32 v21, v23, v21, tcr
.Ltmp274:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v21, v21, v123
.Ltmp275:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v23, 0, v125
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v23, v23, 0x3fb8aa3b
.Ltmp276:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v17, v17, v121
.Ltmp277:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v23, v23
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v25, 0, v127
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v25, v25, 0x3fb8aa3b
.Ltmp278:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v17, v17, v32
.Ltmp279:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v25, v25
.Ltmp280:
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v19, v21, v19
.Ltmp281:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v21, v23, 0x3f800000
.Ltmp282:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v19, v19
.Ltmp283:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v23, v21
.Ltmp284:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v17, v17
	ml_byte_permute_b32 v17, v17, v19, s2
.Ltmp285:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v19, v25, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v21, v21, 0x80000000
	ml_rcp_f32 v25, v19
	ml_fma_f32 v21, v21, v23, 1.0
	ml_fma_f32 v21, v21, v23, v23
	ml_cmp_class_f32 tcr, v23, v28
	ml_csel_b32 v21, v23, v21, tcr
	ml_xor_b32 v19, v19, 0x80000000
	ml_fma_f32 v19, v19, v25, 1.0
	ml_fma_f32 v19, v19, v25, v25
	ml_cmp_class_f32 tcr, v25, v28
	ml_csel_b32 v19, v25, v19, tcr
.Ltmp286:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v19, v19, v127
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v23, v84, v64
	ml_shl_b32 v23, v23, 0x1
	ml_mov_v2s_b32 s4, v23, 0x0
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v21, v21, v125
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v21, v21, v30
	ml_mul_f32 v18, v19, v18
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v19, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[48:49], tmsk
	ml_lsa_store_dword v17, s[0:3], signed v19, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp287:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v17, 0, v126
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v17, v17, 0x3fb8aa3b
.Ltmp288:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v18, v18
.Ltmp289:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v17, v17
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v19, 0, v128
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v19, v19, 0x3fb8aa3b
.Ltmp290:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v21, v21
.Ltmp291:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v19, v19
.Ltmp292:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v23, v102, v64
	ml_shl_b32 v23, v23, 0x1
	ml_mov_v2s_b32 s4, v23, 0x0
.Ltmp293:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v17, v17, 0x3f800000
.Ltmp294:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v18, v21, v18, s2
.Ltmp295:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v21, v17
.Ltmp296:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v23, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[60:61], tmsk
	ml_lsa_store_dword v18, s[0:3], signed v23, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp297:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v18, v19, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v17, v17, 0x80000000
	ml_rcp_f32 v19, v18
	ml_fma_f32 v17, v17, v21, 1.0
	ml_fma_f32 v17, v17, v21, v21
	ml_cmp_class_f32 tcr, v21, v28
	ml_csel_b32 v17, v21, v17, tcr
	ml_xor_b32 v18, v18, 0x80000000
	ml_fma_f32 v18, v18, v19, 1.0
	ml_fma_f32 v18, v18, v19, v19
	ml_cmp_class_f32 tcr, v19, v28
	ml_csel_b32 v18, v19, v18, tcr
.Ltmp298:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v18, v18, v128
.Ltmp299:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v19, 0, v129
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v19, v19, 0x3fb8aa3b
.Ltmp300:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v17, v17, v126
.Ltmp301:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v19, v19
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v21, 0, v131
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v21, v21, 0x3fb8aa3b
.Ltmp302:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v17, v17, v31
.Ltmp303:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v21, v21
.Ltmp304:
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v18, v18, v20
.Ltmp305:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v19, v19, 0x3f800000
.Ltmp306:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v18, v18
.Ltmp307:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v20, v19
.Ltmp308:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v17, v17
	ml_byte_permute_b32 v17, v17, v18, s2
.Ltmp309:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v18, v21, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v19, v19, 0x80000000
	ml_rcp_f32 v21, v18
	ml_fma_f32 v19, v19, v20, 1.0
	ml_fma_f32 v19, v19, v20, v20
	ml_cmp_class_f32 tcr, v20, v28
	ml_csel_b32 v19, v20, v19, tcr
	ml_xor_b32 v18, v18, 0x80000000
	ml_fma_f32 v18, v18, v21, 1.0
	ml_fma_f32 v18, v18, v21, v21
	ml_cmp_class_f32 tcr, v21, v28
	ml_csel_b32 v18, v21, v18, tcr
.Ltmp310:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v18, v18, v131
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v20, v91, v64
	ml_shl_b32 v20, v20, 0x1
	ml_mov_v2s_b32 s4, v20, 0x0
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v19, v19, v129
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v19, v19, v24
	ml_mul_f32 v7, v18, v7
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v18, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[52:53], tmsk
	ml_lsa_store_dword v17, s[0:3], signed v18, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp311:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v17, 0, v130
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v17, v17, 0x3fb8aa3b
.Ltmp312:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v7, v7
.Ltmp313:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v17, v17
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v18, 0, v132
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v18, v18, 0x3fb8aa3b
.Ltmp314:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v19, v19
.Ltmp315:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v18, v18
.Ltmp316:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v20, v109, v64
	ml_shl_b32 v20, v20, 0x1
	ml_mov_v2s_b32 s4, v20, 0x0
.Ltmp317:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v17, v17, 0x3f800000
.Ltmp318:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v7, v19, v7, s2
.Ltmp319:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v19, v17
.Ltmp320:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v20, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[64:65], tmsk
	ml_lsa_store_dword v7, s[0:3], signed v20, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp321:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v7, v18, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v17, v17, 0x80000000
	ml_rcp_f32 v18, v7
	ml_fma_f32 v17, v17, v19, 1.0
	ml_fma_f32 v17, v17, v19, v19
	ml_cmp_class_f32 tcr, v19, v28
	ml_csel_b32 v17, v19, v17, tcr
	ml_xor_b32 v7, v7, 0x80000000
	ml_fma_f32 v7, v7, v18, 1.0
	ml_fma_f32 v7, v7, v18, v18
	ml_cmp_class_f32 tcr, v18, v28
	ml_csel_b32 v7, v18, v7, tcr
.Ltmp322:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v7, v7, v132
.Ltmp323:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v18, 0, v133
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v18, v18, 0x3fb8aa3b
.Ltmp324:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v17, v17, v130
.Ltmp325:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v18, v18
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v19, 0, v135
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v19, v19, 0x3fb8aa3b
.Ltmp326:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v17, v17, v22
.Ltmp327:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v19, v19
.Ltmp328:
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v7, v7, v9
.Ltmp329:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v9, v18, 0x3f800000
.Ltmp330:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v7, v7
.Ltmp331:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v18, v9
.Ltmp332:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v17, v17
	ml_byte_permute_b32 v7, v17, v7, s2
.Ltmp333:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v17, v19, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v9, v9, 0x80000000
	ml_rcp_f32 v19, v17
	ml_fma_f32 v9, v9, v18, 1.0
	ml_fma_f32 v9, v9, v18, v18
	ml_cmp_class_f32 tcr, v18, v28
	ml_csel_b32 v9, v18, v9, tcr
	ml_xor_b32 v17, v17, 0x80000000
	ml_fma_f32 v17, v17, v19, 1.0
	ml_fma_f32 v17, v17, v19, v19
	ml_cmp_class_f32 tcr, v19, v28
	ml_csel_b32 v17, v19, v17, tcr
.Ltmp334:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v17, v17, v135
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v18, v97, v64
	ml_shl_b32 v18, v18, 0x1
	ml_mov_v2s_b32 s4, v18, 0x0
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v9, v9, v133
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v9, v9, v16
	ml_mul_f32 v13, v17, v13
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v16, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[56:57], tmsk
	ml_lsa_store_dword v7, s[0:3], signed v16, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp335:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v7, 0, v134
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v7, v7, 0x3fb8aa3b
.Ltmp336:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v13, v13
.Ltmp337:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v7, v7
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v16, 0, v136
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v16, v16, 0x3fb8aa3b
.Ltmp338:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v9, v9
.Ltmp339:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v16, v16
.Ltmp340:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v17, v114, v64
	ml_shl_b32 v17, v17, 0x1
	ml_mov_v2s_b32 s4, v17, 0x0
.Ltmp341:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v7, v7, 0x3f800000
.Ltmp342:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v9, v9, v13, s2
.Ltmp343:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v13, v7
.Ltmp344:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v17, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[66:67], tmsk
	ml_lsa_store_dword v9, s[0:3], signed v17, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp345:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v9, v16, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v7, v7, 0x80000000
	ml_rcp_f32 v16, v9
	ml_fma_f32 v7, v7, v13, 1.0
	ml_fma_f32 v7, v7, v13, v13
	ml_cmp_class_f32 tcr, v13, v28
	ml_csel_b32 v7, v13, v7, tcr
	ml_xor_b32 v9, v9, 0x80000000
	ml_fma_f32 v9, v9, v16, 1.0
	ml_fma_f32 v9, v9, v16, v16
	ml_cmp_class_f32 tcr, v16, v28
	ml_csel_b32 v9, v16, v9, tcr
.Ltmp346:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v9, v9, v136
.Ltmp347:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v13, 0, v137
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v13, v13, 0x3fb8aa3b
.Ltmp348:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v7, v7, v134
.Ltmp349:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v13, v13
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v16, 0, v139
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v16, v16, 0x3fb8aa3b
.Ltmp350:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v7, v7, v15
.Ltmp351:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v15, v16
.Ltmp352:
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v8, v9, v8
.Ltmp353:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v9, v13, 0x3f800000
.Ltmp354:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v8, v8
.Ltmp355:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v13, v9
.Ltmp356:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v7, v7
	ml_byte_permute_b32 v7, v7, v8, s2
.Ltmp357:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v8, v15, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v9, v9, 0x80000000
	ml_rcp_f32 v15, v8
	ml_fma_f32 v9, v9, v13, 1.0
	ml_fma_f32 v9, v9, v13, v13
	ml_cmp_class_f32 tcr, v13, v28
	ml_csel_b32 v9, v13, v9, tcr
	ml_xor_b32 v8, v8, 0x80000000
	ml_fma_f32 v8, v8, v15, 1.0
	ml_fma_f32 v8, v8, v15, v15
	ml_cmp_class_f32 tcr, v15, v28
	ml_csel_b32 v8, v15, v8, tcr
.Ltmp358:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v8, v8, v139
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v13, v103, v64
	ml_shl_b32 v13, v13, 0x1
	ml_mov_v2s_b32 s4, v13, 0x0
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v9, v9, v137
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v9, v9, v14
	ml_mul_f32 v8, v8, v12
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v12, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[62:63], tmsk
	ml_lsa_store_dword v7, s[0:3], signed v12, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp359:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v7, 0, v138
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v7, v7, 0x3fb8aa3b
.Ltmp360:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v8, v8
.Ltmp361:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v7, v7
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v12, 0, v140
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v12, v12, 0x3fb8aa3b
.Ltmp362:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_cvt_bf16_f32  v9, v9
.Ltmp363:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v12, v12
.Ltmp364:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v13, v119, v64
	ml_shl_b32 v13, v13, 0x1
	ml_mov_v2s_b32 s4, v13, 0x0
.Ltmp365:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v7, v7, 0x3f800000
.Ltmp366:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_byte_permute_b32 v8, v9, v8, s2
.Ltmp367:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v9, v7
.Ltmp368:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_add_i32 v13, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[68:69], tmsk
	ml_lsa_store_dword v8, s[0:3], signed v13, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp369:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v8, v12, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v7, v7, 0x80000000
	ml_rcp_f32 v12, v8
	ml_fma_f32 v7, v7, v9, 1.0
	ml_fma_f32 v7, v7, v9, v9
	ml_cmp_class_f32 tcr, v9, v28
	ml_csel_b32 v7, v9, v7, tcr
	ml_xor_b32 v8, v8, 0x80000000
	ml_fma_f32 v8, v8, v12, 1.0
	ml_fma_f32 v8, v8, v12, v12
	ml_cmp_class_f32 tcr, v12, v28
	ml_csel_b32 v8, v12, v8, tcr
.Ltmp370:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v8, v8, v140
.Ltmp371:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v9, 0, v141
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v9, v9, 0x3fb8aa3b
.Ltmp372:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v7, v7, v138
.Ltmp373:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v9, v9
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v12, 0, v142
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v12, v12, 0x3fb8aa3b
.Ltmp374:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v7, v7, v11
.Ltmp375:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v11, v12
.Ltmp376:
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v4, v8, v4
.Ltmp377:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v8, v9, 0x3f800000
.Ltmp378:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v4, v4
.Ltmp379:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v9, v8
.Ltmp380:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v7, v7
	ml_byte_permute_b32 v4, v7, v4, s2
.Ltmp381:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v7, v11, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v8, v8, 0x80000000
	ml_rcp_f32 v11, v7
	ml_fma_f32 v8, v8, v9, 1.0
	ml_fma_f32 v8, v8, v9, v9
	ml_cmp_class_f32 tcr, v9, v28
	ml_csel_b32 v8, v9, v8, tcr
	ml_xor_b32 v7, v7, 0x80000000
	ml_fma_f32 v7, v7, v11, 1.0
	ml_fma_f32 v7, v7, v11, v11
	ml_cmp_class_f32 tcr, v11, v28
	ml_csel_b32 v7, v11, v7, tcr
.Ltmp382:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v7, v7, v142
.Ltmp383:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v9, 0, v143
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v9, v9, 0x3fb8aa3b
.Ltmp384:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v8, v8, v141
.Ltmp385:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v9, v9
	.loc	2 72 30 is_stmt 0               ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v11, 0, v144
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v11, v11, 0x3fb8aa3b
.Ltmp386:
	.loc	1 48 22 is_stmt 1               ; candidate.py:48:22
	ml_mul_f32 v6, v8, v6
.Ltmp387:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v8, v11
.Ltmp388:
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v7, v7, v10
.Ltmp389:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v9, v9, 0x3f800000
.Ltmp390:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v7, v7
.Ltmp391:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v10, v9
.Ltmp392:
	.loc	1 49 35                         ; candidate.py:49:35
	ml_cvt_bf16_f32  v6, v6
	ml_byte_permute_b32 v6, v6, v7, s2
.Ltmp393:
	.loc	2 72 20                         ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v7, v8, 0x3f800000
	.loc	2 72 16 is_stmt 0               ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_xor_b32 v8, v9, 0x80000000
	ml_rcp_f32 v9, v7
	ml_fma_f32 v8, v8, v10, 1.0
	ml_fma_f32 v8, v8, v10, v10
	ml_cmp_class_f32 tcr, v10, v28
	ml_csel_b32 v8, v10, v8, tcr
	ml_xor_b32 v7, v7, 0x80000000
	ml_fma_f32 v7, v7, v9, 1.0
	ml_fma_f32 v7, v7, v9, v9
	ml_cmp_class_f32 tcr, v9, v28
	ml_csel_b32 v7, v9, v7, tcr
.Ltmp394:
	.loc	1 46 22 is_stmt 1               ; candidate.py:46:22
	ml_mul_f32 v7, v7, v144
	ml_mul_f32 v8, v8, v143
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v3, v8, v3
	ml_mul_f32 v5, v7, v5
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v7, v81, v64
	ml_shl_b32 v7, v7, 0x1
	ml_mov_v2s_b32 s4, v7, 0x0
	ml_cvt_bf16_f32  v5, v5
	ml_cvt_bf16_f32  v3, v3
	ml_byte_permute_b32 v3, v3, v5, s2
	ml_add_i32 v5, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[44:45], tmsk
	ml_lsa_store_dword v4, s[0:3], signed v5, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp395:
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v4, 0, v146
	.loc	2 72 29 is_stmt 0               ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_mul_f32 v4, v4, 0x3fb8aa3b
	.loc	2 72 30                         ; standard.py:72:30 @[ candidate.py:45:26 ]
	ml_sub_f32 v5, 0, v147
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v4, v4
	ml_mul_f32 v5, v5, 0x3fb8aa3b
.Ltmp396:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_sub_i32 v7, v104, v64
	ml_shl_b32 v7, v7, 0x1
	ml_mov_v2s_b32 s4, v7, 0x0
.Ltmp397:
	.loc	2 72 29                         ; standard.py:72:29 @[ candidate.py:45:26 ]
	ml_exp_f32 v5, v5
	.loc	2 72 20 is_stmt 0               ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v4, v4, 0x3f800000
.Ltmp398:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_sub_i32 v7, v124, v64
	ml_shl_b32 v7, v7, 0x1
	ml_mov_v2s_b32 s5, v7, 0x0
	ml_add_i32 v7, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[58:59], tmsk
	ml_lsa_store_dword v6, s[0:3], signed v7, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp399:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v6, v4
	.loc	2 72 20 is_stmt 0               ; standard.py:72:20 @[ candidate.py:45:26 ]
	ml_add_f32 v5, v5, 0x3f800000
.Ltmp400:
	.loc	1 49 35 is_stmt 1               ; candidate.py:49:35
	ml_add_i32 v7, s5, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[70:71], tmsk
	ml_lsa_store_dword v3, s[0:3], signed v7, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
.Ltmp401:
	.loc	2 72 16                         ; standard.py:72:16 @[ candidate.py:45:26 ]
	ml_rcp_f32 v3, v5
	ml_xor_b32 v4, v4, 0x80000000
	ml_fma_f32 v4, v4, v6, 1.0
	ml_fma_f32 v4, v4, v6, v6
	ml_cmp_class_f32 tcr, v6, v28
	ml_csel_b32 v4, v6, v4, tcr
	ml_cmp_class_f32 tcr, v3, v28
	ml_xor_b32 v5, v5, 0x80000000
	ml_fma_f32 v5, v5, v3, 1.0
	ml_fma_f32 v5, v5, v3, v3
	ml_csel_b32 v3, v3, v5, tcr
.Ltmp402:
	.loc	1 46 22                         ; candidate.py:46:22
	ml_mul_f32 v3, v3, v147
	ml_mul_f32 v4, v4, v146
	.loc	1 48 22                         ; candidate.py:48:22
	ml_mul_f32 v2, v4, v2
	ml_mul_f32 v1, v3, v1
	.loc	1 49 35                         ; candidate.py:49:35
	ml_sub_i32 v3, v145, v64
	ml_shl_b32 v3, v3, 0x1
	ml_mov_v2s_b32 s4, v3, 0x0
	ml_cvt_bf16_f32  v1, v1
	ml_cvt_bf16_f32  v2, v2
	ml_byte_permute_b32 v1, v2, v1, s2
	ml_add_i32 v0, s4, v0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[72:73], tmsk
	ml_lsa_store_dword v1, s[0:3], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 40 4                          ; candidate.py:40:4
	sl_eop 
.Ltmp403:
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	half_mm.kd
	.type	half_mm.kd,@object
	.size	half_mm.kd, 64
half_mm.kd:
	.asciz	"\000\000\000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	half_mm@rel64-half_mm.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	537194
	.asciz	"\003\000\224\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	half_mm, .Lfunc_end0-half_mm
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 18256
; NumSgprs: 80
; NumVgprs: 169
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 9
; VGPRBlocks: 42
; NumSGPRsForWarpsPerNU: 76
; NumVGPRsForWarpsPerNR: 169
; ReqNTIDx: 0
; MaxNTIDx: 0
; MinCTASm: 0
; ActiveWarp: 1
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
	.long	206                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0xc7 DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"candidate.py"                  ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/workspace/experiments/minicpm-s2/framework/20261026T075700478338Z-biv150-gate-partial-fusion-component/source" ; DW_AT_comp_dir
	.byte	0
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.byte	2                               ; Abbrev [2] 0xa5:0xa DW_TAG_subprogram
	.ascii	"half_mm"                       ; DW_AT_name
	.byte	0
	.byte	1                               ; DW_AT_inline
	.byte	3                               ; Abbrev [3] 0xaf:0x22 DW_TAG_subprogram
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.long	165                             ; DW_AT_abstract_origin
	.byte	4                               ; Abbrev [4] 0xc4:0xc DW_TAG_inlined_subroutine
	.long	165                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges0                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	45                              ; DW_AT_call_line
	.byte	26                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	0                               ; End Of Children Mark
	.section	.debug_ranges,"",@progbits
.Ldebug_ranges0:
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
	.quad	.Ltmp12-.Lfunc_begin0
	.quad	.Ltmp13-.Lfunc_begin0
	.quad	.Ltmp14-.Lfunc_begin0
	.quad	.Ltmp15-.Lfunc_begin0
	.quad	.Ltmp16-.Lfunc_begin0
	.quad	.Ltmp17-.Lfunc_begin0
	.quad	.Ltmp18-.Lfunc_begin0
	.quad	.Ltmp19-.Lfunc_begin0
	.quad	.Ltmp20-.Lfunc_begin0
	.quad	.Ltmp21-.Lfunc_begin0
	.quad	.Ltmp22-.Lfunc_begin0
	.quad	.Ltmp23-.Lfunc_begin0
	.quad	.Ltmp24-.Lfunc_begin0
	.quad	.Ltmp25-.Lfunc_begin0
	.quad	.Ltmp26-.Lfunc_begin0
	.quad	.Ltmp27-.Lfunc_begin0
	.quad	.Ltmp28-.Lfunc_begin0
	.quad	.Ltmp29-.Lfunc_begin0
	.quad	.Ltmp30-.Lfunc_begin0
	.quad	.Ltmp31-.Lfunc_begin0
	.quad	.Ltmp32-.Lfunc_begin0
	.quad	.Ltmp33-.Lfunc_begin0
	.quad	.Ltmp34-.Lfunc_begin0
	.quad	.Ltmp35-.Lfunc_begin0
	.quad	.Ltmp36-.Lfunc_begin0
	.quad	.Ltmp37-.Lfunc_begin0
	.quad	.Ltmp38-.Lfunc_begin0
	.quad	.Ltmp39-.Lfunc_begin0
	.quad	.Ltmp40-.Lfunc_begin0
	.quad	.Ltmp41-.Lfunc_begin0
	.quad	.Ltmp42-.Lfunc_begin0
	.quad	.Ltmp43-.Lfunc_begin0
	.quad	.Ltmp44-.Lfunc_begin0
	.quad	.Ltmp45-.Lfunc_begin0
	.quad	.Ltmp46-.Lfunc_begin0
	.quad	.Ltmp47-.Lfunc_begin0
	.quad	.Ltmp48-.Lfunc_begin0
	.quad	.Ltmp49-.Lfunc_begin0
	.quad	.Ltmp50-.Lfunc_begin0
	.quad	.Ltmp51-.Lfunc_begin0
	.quad	.Ltmp52-.Lfunc_begin0
	.quad	.Ltmp53-.Lfunc_begin0
	.quad	.Ltmp54-.Lfunc_begin0
	.quad	.Ltmp55-.Lfunc_begin0
	.quad	.Ltmp56-.Lfunc_begin0
	.quad	.Ltmp57-.Lfunc_begin0
	.quad	.Ltmp58-.Lfunc_begin0
	.quad	.Ltmp59-.Lfunc_begin0
	.quad	.Ltmp60-.Lfunc_begin0
	.quad	.Ltmp61-.Lfunc_begin0
	.quad	.Ltmp62-.Lfunc_begin0
	.quad	.Ltmp63-.Lfunc_begin0
	.quad	.Ltmp64-.Lfunc_begin0
	.quad	.Ltmp65-.Lfunc_begin0
	.quad	.Ltmp66-.Lfunc_begin0
	.quad	.Ltmp67-.Lfunc_begin0
	.quad	.Ltmp68-.Lfunc_begin0
	.quad	.Ltmp69-.Lfunc_begin0
	.quad	.Ltmp70-.Lfunc_begin0
	.quad	.Ltmp71-.Lfunc_begin0
	.quad	.Ltmp72-.Lfunc_begin0
	.quad	.Ltmp73-.Lfunc_begin0
	.quad	.Ltmp74-.Lfunc_begin0
	.quad	.Ltmp75-.Lfunc_begin0
	.quad	.Ltmp76-.Lfunc_begin0
	.quad	.Ltmp77-.Lfunc_begin0
	.quad	.Ltmp78-.Lfunc_begin0
	.quad	.Ltmp79-.Lfunc_begin0
	.quad	.Ltmp80-.Lfunc_begin0
	.quad	.Ltmp81-.Lfunc_begin0
	.quad	.Ltmp82-.Lfunc_begin0
	.quad	.Ltmp83-.Lfunc_begin0
	.quad	.Ltmp84-.Lfunc_begin0
	.quad	.Ltmp85-.Lfunc_begin0
	.quad	.Ltmp86-.Lfunc_begin0
	.quad	.Ltmp87-.Lfunc_begin0
	.quad	.Ltmp88-.Lfunc_begin0
	.quad	.Ltmp89-.Lfunc_begin0
	.quad	.Ltmp90-.Lfunc_begin0
	.quad	.Ltmp91-.Lfunc_begin0
	.quad	.Ltmp92-.Lfunc_begin0
	.quad	.Ltmp93-.Lfunc_begin0
	.quad	.Ltmp94-.Lfunc_begin0
	.quad	.Ltmp95-.Lfunc_begin0
	.quad	.Ltmp96-.Lfunc_begin0
	.quad	.Ltmp97-.Lfunc_begin0
	.quad	.Ltmp98-.Lfunc_begin0
	.quad	.Ltmp99-.Lfunc_begin0
	.quad	.Ltmp100-.Lfunc_begin0
	.quad	.Ltmp101-.Lfunc_begin0
	.quad	.Ltmp102-.Lfunc_begin0
	.quad	.Ltmp103-.Lfunc_begin0
	.quad	.Ltmp104-.Lfunc_begin0
	.quad	.Ltmp105-.Lfunc_begin0
	.quad	.Ltmp106-.Lfunc_begin0
	.quad	.Ltmp107-.Lfunc_begin0
	.quad	.Ltmp108-.Lfunc_begin0
	.quad	.Ltmp109-.Lfunc_begin0
	.quad	.Ltmp110-.Lfunc_begin0
	.quad	.Ltmp111-.Lfunc_begin0
	.quad	.Ltmp112-.Lfunc_begin0
	.quad	.Ltmp113-.Lfunc_begin0
	.quad	.Ltmp114-.Lfunc_begin0
	.quad	.Ltmp115-.Lfunc_begin0
	.quad	.Ltmp116-.Lfunc_begin0
	.quad	.Ltmp117-.Lfunc_begin0
	.quad	.Ltmp118-.Lfunc_begin0
	.quad	.Ltmp119-.Lfunc_begin0
	.quad	.Ltmp120-.Lfunc_begin0
	.quad	.Ltmp121-.Lfunc_begin0
	.quad	.Ltmp122-.Lfunc_begin0
	.quad	.Ltmp123-.Lfunc_begin0
	.quad	.Ltmp124-.Lfunc_begin0
	.quad	.Ltmp125-.Lfunc_begin0
	.quad	.Ltmp126-.Lfunc_begin0
	.quad	.Ltmp127-.Lfunc_begin0
	.quad	.Ltmp128-.Lfunc_begin0
	.quad	.Ltmp129-.Lfunc_begin0
	.quad	.Ltmp130-.Lfunc_begin0
	.quad	.Ltmp131-.Lfunc_begin0
	.quad	.Ltmp132-.Lfunc_begin0
	.quad	.Ltmp133-.Lfunc_begin0
	.quad	.Ltmp134-.Lfunc_begin0
	.quad	.Ltmp135-.Lfunc_begin0
	.quad	.Ltmp136-.Lfunc_begin0
	.quad	.Ltmp137-.Lfunc_begin0
	.quad	.Ltmp138-.Lfunc_begin0
	.quad	.Ltmp139-.Lfunc_begin0
	.quad	.Ltmp140-.Lfunc_begin0
	.quad	.Ltmp141-.Lfunc_begin0
	.quad	.Ltmp142-.Lfunc_begin0
	.quad	.Ltmp143-.Lfunc_begin0
	.quad	.Ltmp144-.Lfunc_begin0
	.quad	.Ltmp145-.Lfunc_begin0
	.quad	.Ltmp146-.Lfunc_begin0
	.quad	.Ltmp147-.Lfunc_begin0
	.quad	.Ltmp148-.Lfunc_begin0
	.quad	.Ltmp149-.Lfunc_begin0
	.quad	.Ltmp150-.Lfunc_begin0
	.quad	.Ltmp151-.Lfunc_begin0
	.quad	.Ltmp152-.Lfunc_begin0
	.quad	.Ltmp153-.Lfunc_begin0
	.quad	.Ltmp154-.Lfunc_begin0
	.quad	.Ltmp155-.Lfunc_begin0
	.quad	.Ltmp156-.Lfunc_begin0
	.quad	.Ltmp157-.Lfunc_begin0
	.quad	.Ltmp158-.Lfunc_begin0
	.quad	.Ltmp159-.Lfunc_begin0
	.quad	.Ltmp160-.Lfunc_begin0
	.quad	.Ltmp161-.Lfunc_begin0
	.quad	.Ltmp162-.Lfunc_begin0
	.quad	.Ltmp163-.Lfunc_begin0
	.quad	.Ltmp164-.Lfunc_begin0
	.quad	.Ltmp165-.Lfunc_begin0
	.quad	.Ltmp166-.Lfunc_begin0
	.quad	.Ltmp167-.Lfunc_begin0
	.quad	.Ltmp168-.Lfunc_begin0
	.quad	.Ltmp169-.Lfunc_begin0
	.quad	.Ltmp170-.Lfunc_begin0
	.quad	.Ltmp171-.Lfunc_begin0
	.quad	.Ltmp172-.Lfunc_begin0
	.quad	.Ltmp173-.Lfunc_begin0
	.quad	.Ltmp174-.Lfunc_begin0
	.quad	.Ltmp175-.Lfunc_begin0
	.quad	.Ltmp176-.Lfunc_begin0
	.quad	.Ltmp177-.Lfunc_begin0
	.quad	.Ltmp178-.Lfunc_begin0
	.quad	.Ltmp179-.Lfunc_begin0
	.quad	.Ltmp180-.Lfunc_begin0
	.quad	.Ltmp181-.Lfunc_begin0
	.quad	.Ltmp182-.Lfunc_begin0
	.quad	.Ltmp183-.Lfunc_begin0
	.quad	.Ltmp184-.Lfunc_begin0
	.quad	.Ltmp185-.Lfunc_begin0
	.quad	.Ltmp186-.Lfunc_begin0
	.quad	.Ltmp187-.Lfunc_begin0
	.quad	.Ltmp188-.Lfunc_begin0
	.quad	.Ltmp189-.Lfunc_begin0
	.quad	.Ltmp190-.Lfunc_begin0
	.quad	.Ltmp191-.Lfunc_begin0
	.quad	.Ltmp192-.Lfunc_begin0
	.quad	.Ltmp193-.Lfunc_begin0
	.quad	.Ltmp194-.Lfunc_begin0
	.quad	.Ltmp195-.Lfunc_begin0
	.quad	.Ltmp196-.Lfunc_begin0
	.quad	.Ltmp197-.Lfunc_begin0
	.quad	.Ltmp198-.Lfunc_begin0
	.quad	.Ltmp199-.Lfunc_begin0
	.quad	.Ltmp200-.Lfunc_begin0
	.quad	.Ltmp201-.Lfunc_begin0
	.quad	.Ltmp202-.Lfunc_begin0
	.quad	.Ltmp203-.Lfunc_begin0
	.quad	.Ltmp204-.Lfunc_begin0
	.quad	.Ltmp205-.Lfunc_begin0
	.quad	.Ltmp206-.Lfunc_begin0
	.quad	.Ltmp207-.Lfunc_begin0
	.quad	.Ltmp208-.Lfunc_begin0
	.quad	.Ltmp209-.Lfunc_begin0
	.quad	.Ltmp210-.Lfunc_begin0
	.quad	.Ltmp211-.Lfunc_begin0
	.quad	.Ltmp212-.Lfunc_begin0
	.quad	.Ltmp213-.Lfunc_begin0
	.quad	.Ltmp214-.Lfunc_begin0
	.quad	.Ltmp215-.Lfunc_begin0
	.quad	.Ltmp216-.Lfunc_begin0
	.quad	.Ltmp217-.Lfunc_begin0
	.quad	.Ltmp218-.Lfunc_begin0
	.quad	.Ltmp219-.Lfunc_begin0
	.quad	.Ltmp220-.Lfunc_begin0
	.quad	.Ltmp221-.Lfunc_begin0
	.quad	.Ltmp222-.Lfunc_begin0
	.quad	.Ltmp223-.Lfunc_begin0
	.quad	.Ltmp224-.Lfunc_begin0
	.quad	.Ltmp225-.Lfunc_begin0
	.quad	.Ltmp226-.Lfunc_begin0
	.quad	.Ltmp227-.Lfunc_begin0
	.quad	.Ltmp228-.Lfunc_begin0
	.quad	.Ltmp229-.Lfunc_begin0
	.quad	.Ltmp230-.Lfunc_begin0
	.quad	.Ltmp231-.Lfunc_begin0
	.quad	.Ltmp232-.Lfunc_begin0
	.quad	.Ltmp233-.Lfunc_begin0
	.quad	.Ltmp234-.Lfunc_begin0
	.quad	.Ltmp235-.Lfunc_begin0
	.quad	.Ltmp236-.Lfunc_begin0
	.quad	.Ltmp237-.Lfunc_begin0
	.quad	.Ltmp238-.Lfunc_begin0
	.quad	.Ltmp239-.Lfunc_begin0
	.quad	.Ltmp240-.Lfunc_begin0
	.quad	.Ltmp241-.Lfunc_begin0
	.quad	.Ltmp242-.Lfunc_begin0
	.quad	.Ltmp243-.Lfunc_begin0
	.quad	.Ltmp244-.Lfunc_begin0
	.quad	.Ltmp245-.Lfunc_begin0
	.quad	.Ltmp246-.Lfunc_begin0
	.quad	.Ltmp247-.Lfunc_begin0
	.quad	.Ltmp248-.Lfunc_begin0
	.quad	.Ltmp249-.Lfunc_begin0
	.quad	.Ltmp250-.Lfunc_begin0
	.quad	.Ltmp251-.Lfunc_begin0
	.quad	.Ltmp252-.Lfunc_begin0
	.quad	.Ltmp253-.Lfunc_begin0
	.quad	.Ltmp254-.Lfunc_begin0
	.quad	.Ltmp255-.Lfunc_begin0
	.quad	.Ltmp256-.Lfunc_begin0
	.quad	.Ltmp257-.Lfunc_begin0
	.quad	.Ltmp258-.Lfunc_begin0
	.quad	.Ltmp259-.Lfunc_begin0
	.quad	.Ltmp260-.Lfunc_begin0
	.quad	.Ltmp261-.Lfunc_begin0
	.quad	.Ltmp262-.Lfunc_begin0
	.quad	.Ltmp263-.Lfunc_begin0
	.quad	.Ltmp264-.Lfunc_begin0
	.quad	.Ltmp265-.Lfunc_begin0
	.quad	.Ltmp266-.Lfunc_begin0
	.quad	.Ltmp267-.Lfunc_begin0
	.quad	.Ltmp268-.Lfunc_begin0
	.quad	.Ltmp269-.Lfunc_begin0
	.quad	.Ltmp270-.Lfunc_begin0
	.quad	.Ltmp271-.Lfunc_begin0
	.quad	.Ltmp272-.Lfunc_begin0
	.quad	.Ltmp273-.Lfunc_begin0
	.quad	.Ltmp274-.Lfunc_begin0
	.quad	.Ltmp275-.Lfunc_begin0
	.quad	.Ltmp276-.Lfunc_begin0
	.quad	.Ltmp277-.Lfunc_begin0
	.quad	.Ltmp278-.Lfunc_begin0
	.quad	.Ltmp279-.Lfunc_begin0
	.quad	.Ltmp280-.Lfunc_begin0
	.quad	.Ltmp281-.Lfunc_begin0
	.quad	.Ltmp282-.Lfunc_begin0
	.quad	.Ltmp283-.Lfunc_begin0
	.quad	.Ltmp284-.Lfunc_begin0
	.quad	.Ltmp285-.Lfunc_begin0
	.quad	.Ltmp286-.Lfunc_begin0
	.quad	.Ltmp287-.Lfunc_begin0
	.quad	.Ltmp288-.Lfunc_begin0
	.quad	.Ltmp289-.Lfunc_begin0
	.quad	.Ltmp290-.Lfunc_begin0
	.quad	.Ltmp291-.Lfunc_begin0
	.quad	.Ltmp292-.Lfunc_begin0
	.quad	.Ltmp293-.Lfunc_begin0
	.quad	.Ltmp294-.Lfunc_begin0
	.quad	.Ltmp295-.Lfunc_begin0
	.quad	.Ltmp296-.Lfunc_begin0
	.quad	.Ltmp297-.Lfunc_begin0
	.quad	.Ltmp298-.Lfunc_begin0
	.quad	.Ltmp299-.Lfunc_begin0
	.quad	.Ltmp300-.Lfunc_begin0
	.quad	.Ltmp301-.Lfunc_begin0
	.quad	.Ltmp302-.Lfunc_begin0
	.quad	.Ltmp303-.Lfunc_begin0
	.quad	.Ltmp304-.Lfunc_begin0
	.quad	.Ltmp305-.Lfunc_begin0
	.quad	.Ltmp306-.Lfunc_begin0
	.quad	.Ltmp307-.Lfunc_begin0
	.quad	.Ltmp308-.Lfunc_begin0
	.quad	.Ltmp309-.Lfunc_begin0
	.quad	.Ltmp310-.Lfunc_begin0
	.quad	.Ltmp311-.Lfunc_begin0
	.quad	.Ltmp312-.Lfunc_begin0
	.quad	.Ltmp313-.Lfunc_begin0
	.quad	.Ltmp314-.Lfunc_begin0
	.quad	.Ltmp315-.Lfunc_begin0
	.quad	.Ltmp316-.Lfunc_begin0
	.quad	.Ltmp317-.Lfunc_begin0
	.quad	.Ltmp318-.Lfunc_begin0
	.quad	.Ltmp319-.Lfunc_begin0
	.quad	.Ltmp320-.Lfunc_begin0
	.quad	.Ltmp321-.Lfunc_begin0
	.quad	.Ltmp322-.Lfunc_begin0
	.quad	.Ltmp323-.Lfunc_begin0
	.quad	.Ltmp324-.Lfunc_begin0
	.quad	.Ltmp325-.Lfunc_begin0
	.quad	.Ltmp326-.Lfunc_begin0
	.quad	.Ltmp327-.Lfunc_begin0
	.quad	.Ltmp328-.Lfunc_begin0
	.quad	.Ltmp329-.Lfunc_begin0
	.quad	.Ltmp330-.Lfunc_begin0
	.quad	.Ltmp331-.Lfunc_begin0
	.quad	.Ltmp332-.Lfunc_begin0
	.quad	.Ltmp333-.Lfunc_begin0
	.quad	.Ltmp334-.Lfunc_begin0
	.quad	.Ltmp335-.Lfunc_begin0
	.quad	.Ltmp336-.Lfunc_begin0
	.quad	.Ltmp337-.Lfunc_begin0
	.quad	.Ltmp338-.Lfunc_begin0
	.quad	.Ltmp339-.Lfunc_begin0
	.quad	.Ltmp340-.Lfunc_begin0
	.quad	.Ltmp341-.Lfunc_begin0
	.quad	.Ltmp342-.Lfunc_begin0
	.quad	.Ltmp343-.Lfunc_begin0
	.quad	.Ltmp344-.Lfunc_begin0
	.quad	.Ltmp345-.Lfunc_begin0
	.quad	.Ltmp346-.Lfunc_begin0
	.quad	.Ltmp347-.Lfunc_begin0
	.quad	.Ltmp348-.Lfunc_begin0
	.quad	.Ltmp349-.Lfunc_begin0
	.quad	.Ltmp350-.Lfunc_begin0
	.quad	.Ltmp351-.Lfunc_begin0
	.quad	.Ltmp352-.Lfunc_begin0
	.quad	.Ltmp353-.Lfunc_begin0
	.quad	.Ltmp354-.Lfunc_begin0
	.quad	.Ltmp355-.Lfunc_begin0
	.quad	.Ltmp356-.Lfunc_begin0
	.quad	.Ltmp357-.Lfunc_begin0
	.quad	.Ltmp358-.Lfunc_begin0
	.quad	.Ltmp359-.Lfunc_begin0
	.quad	.Ltmp360-.Lfunc_begin0
	.quad	.Ltmp361-.Lfunc_begin0
	.quad	.Ltmp362-.Lfunc_begin0
	.quad	.Ltmp363-.Lfunc_begin0
	.quad	.Ltmp364-.Lfunc_begin0
	.quad	.Ltmp365-.Lfunc_begin0
	.quad	.Ltmp366-.Lfunc_begin0
	.quad	.Ltmp367-.Lfunc_begin0
	.quad	.Ltmp368-.Lfunc_begin0
	.quad	.Ltmp369-.Lfunc_begin0
	.quad	.Ltmp370-.Lfunc_begin0
	.quad	.Ltmp371-.Lfunc_begin0
	.quad	.Ltmp372-.Lfunc_begin0
	.quad	.Ltmp373-.Lfunc_begin0
	.quad	.Ltmp374-.Lfunc_begin0
	.quad	.Ltmp375-.Lfunc_begin0
	.quad	.Ltmp376-.Lfunc_begin0
	.quad	.Ltmp377-.Lfunc_begin0
	.quad	.Ltmp378-.Lfunc_begin0
	.quad	.Ltmp379-.Lfunc_begin0
	.quad	.Ltmp380-.Lfunc_begin0
	.quad	.Ltmp381-.Lfunc_begin0
	.quad	.Ltmp382-.Lfunc_begin0
	.quad	.Ltmp383-.Lfunc_begin0
	.quad	.Ltmp384-.Lfunc_begin0
	.quad	.Ltmp385-.Lfunc_begin0
	.quad	.Ltmp386-.Lfunc_begin0
	.quad	.Ltmp387-.Lfunc_begin0
	.quad	.Ltmp388-.Lfunc_begin0
	.quad	.Ltmp389-.Lfunc_begin0
	.quad	.Ltmp390-.Lfunc_begin0
	.quad	.Ltmp391-.Lfunc_begin0
	.quad	.Ltmp392-.Lfunc_begin0
	.quad	.Ltmp393-.Lfunc_begin0
	.quad	.Ltmp394-.Lfunc_begin0
	.quad	.Ltmp395-.Lfunc_begin0
	.quad	.Ltmp396-.Lfunc_begin0
	.quad	.Ltmp397-.Lfunc_begin0
	.quad	.Ltmp398-.Lfunc_begin0
	.quad	.Ltmp399-.Lfunc_begin0
	.quad	.Ltmp400-.Lfunc_begin0
	.quad	.Ltmp401-.Lfunc_begin0
	.quad	.Ltmp402-.Lfunc_begin0
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
      - .address_space:  global
        .name:           KArg_3
        .offset:         24
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_4
        .offset:         32
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_5
        .offset:         40
        .size:           8
        .value_kind:     global_buffer
    .group_segment_fixed_size: 0
    .kernarg_segment_align: 8
    .kernarg_segment_size: 48
    .max_flat_workgroup_size: 0
    .name:           half_mm
    .private_segment_fixed_size: 0
    .sgpr_count:     80
    .sgpr_spill_count: 0
    .symbol:         half_mm.kd
    .vgpr_count:     169
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
