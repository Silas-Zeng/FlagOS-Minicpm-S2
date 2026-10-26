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
		granulated_workitem_vgpr_count = 20
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
		kernarg_segment_byte_size = 48
		workgroup_fbarrier_count = 0
		warp_sgpr_count = 36
		workitem_vgpr_count = 83
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
	sl_mov_b32 s12, tcr_lo
	ml_vrf_init_u32 v64, tcr
.Ltmp0:
	.loc	1 12 24 prologue_end            ; candidate.py:12:24
	sl_lsa_load_b32x16 s[16:31], s[4:5], noreg, #0, ca
	.loc	1 16 22                         ; candidate.py:16:22
	sl_mulh_u32 s0, s6, 0x2aaaaaab
	sl_srl_b32 {s1, wcr}, s0, 0x5
	.loc	1 17 37                         ; candidate.py:17:37
	sl_mull_u32 s14, s1, 0x8
	sl_mov_b32 s0, 0x8
	.loc	1 17 26 is_stmt 0               ; candidate.py:17:26
	sl_sub_i32 s7, s0, s14
	.loc	1 18 30 is_stmt 1               ; candidate.py:18:30
	sl_abs_i32 s10, s7
	ml_cvt_f32_u32  v0, s10
	sl_mov_b32 s13, 0x0
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
	ml_shl_b32 v0, v64, 0x2
	.loc	1 18 30                         ; candidate.py:18:30
	sl_mul_u64_u32 s[2:3], s4, s10
	sl_neg_i32 s1, s2
	sl_cmp_eq_u32 wcr, s3, 0x0
	sl_csel_b32 s1, s1, s2, wcr
	sl_mul_u64_u32 s[2:3], s1, s4
	sl_add_i32 s1, s4, s3
	sl_sub_i32 s2, s4, s3
	sl_csel_b32 s15, s1, s2, wcr
	sl_mul_u64_u32 s[2:3], s15, s6
	sl_mull_u32 s1, s3, s10
	sl_wait smcnt(0)
	sl_sub_i32 s22, s6, s1
	sl_cmp_ge_u32 wcr, s22, s10
	sl_sub_bi_u64 s[2:3], s[8:9], s[8:9], wcr
	sl_cmp_ge_u32 wcr, s6, s1
	sl_sub_bi_u32 s1, s8, s8, wcr
	sl_sub_bi_u64 s[4:5], s[8:9], s[8:9], wcr
	sl_and_b64 {s[4:5], wcr}, s[2:3], s[4:5]
	sl_mov_b32 s2, 0xffffffff
	sl_or_b32 {s4, wcr}, s4, s5
	sl_csel_b32 s3, s2, 0x0, wcr
	sl_cmp_eq_u32 wcr, s3, 0x0
	sl_sub_i32 s3, s22, s10
	sl_add_i32 s4, s22, s10
	sl_csel_b32 s3, s22, s3, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s3, s4, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s3, s2, s1, wcr
	.loc	1 19 26                         ; candidate.py:19:26
	sl_xor_b32 {s1, wcr}, s11, s7
	sl_sra_b32 {s22, wcr}, s1, 0x1f
	sl_abs_i32 s1, s11
	sl_mul_u64_u32 s[4:5], s15, s1
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
	sl_xor_b32 {s1, wcr}, s1, s22
	sl_sub_i32 s1, s1, s22
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s4, s2, s1, wcr
	.loc	1 18 24                         ; candidate.py:18:24
	sl_add_i32 s0, s3, s14
	.loc	1 20 14                         ; candidate.py:20:14
	sl_mull_u32 s14, s0, 0x100
	.loc	1 20 32 is_stmt 0               ; candidate.py:20:32
	sl_bfe2_b32 s5, tcr_lo, 0x86
	.loc	1 22 48 is_stmt 1               ; candidate.py:22:48
	sl_mulh_i32 s0, s14, 0x81228dbf
	sl_add_i32 s0, s0, s14
	sl_srl_b32 {s1, wcr}, s0, 0x1f
	sl_srl_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s1
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s0, s14, s0
	.loc	1 25 28                         ; candidate.py:25:28
	sl_mull_u32 s0, s0, 0x800
	.loc	1 25 13 is_stmt 0               ; candidate.py:25:13
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[0:1], s[16:17], s[0:1]
	sl_mov_b32 s3, 0x1000
	.loc	1 31 20 is_stmt 1               ; candidate.py:31:20
	sl_mull_u32 s15, s5, 0x400
	sl_mull_u32 s10, s5, 0x10000
	sl_mov_b32 s11, s15
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[10:11], 0x0, 0x0, 0x0, 0x1
	.loc	1 21 14                         ; candidate.py:21:14
	sl_mull_u32 s16, s4, 0x100
	.loc	1 23 48                         ; candidate.py:23:48
	sl_mulh_i32 s4, s16, 0x2aaaaaab
	sl_srl_b32 {s5, wcr}, s4, 0x1f
	sl_srl_b32 {s4, wcr}, s4, 0xa
	sl_add_i32 s4, s4, s5
	sl_mull_u32 s4, s4, 0x1800
	sl_sub_i32 s4, s16, s4
	.loc	1 26 42                         ; candidate.py:26:42
	sl_mull_u32 s4, s4, 0x800
	.loc	1 26 27 is_stmt 0               ; candidate.py:26:27
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x1
	sl_add_i64 s[4:5], s[18:19], s[4:5]
	.loc	1 32 20 is_stmt 1               ; candidate.py:32:20
	sl_mov_b64 s[6:7], s[2:3]
	sl_add_i32 s11, s15, 0x8000
	sl_sme_load_16x1b64_col s[4:7], s[10:11], 0x0, 0x0, 0x0, 0x1
	.loc	1 20 32                         ; candidate.py:20:32
	sl_and_b32 {s17, wcr}, tcr_lo, 0xc0
	ml_and_b32 v65, v0, 0xcfc
	ml_shl_b32 v1, v64, 0x6
	ml_and_b32 v1, v1, 0x300
	sl_mull_u32 s6, s17, 0x10
	ml_and_b32 v0, v0, 0xfc
	ml_anyop3_b32 v66, s6, v1, v0, 0xfffffffe
	ml_xor_b32 v67, v66, 0x10
	ml_xor_b32 v68, v66, 0x20
	ml_xor_b32 v69, v66, 0x30
	.loc	1 30 19                         ; candidate.py:30:19
	sl_add_i64 s[4:5], s[4:5], 0x40
	sl_add_i64 s[0:1], s[0:1], 0x40
	sl_mov_b32 s18, 0x40
	ml_mov_b32 v56, 0x0
	ml_xor_b32 v70, v65, 0x80
	sl_mov_b32 s19, s2
	ml_mov_b32 v57, 0x0
	ml_mov_b32 v58, 0x0
	ml_mov_b32 v59, 0x0
	ml_mov_b32 v60, 0x0
	ml_mov_b32 v61, 0x0
	ml_mov_b32 v62, 0x0
	ml_mov_b32 v63, 0x0
	ml_mov_b32 v52, 0x0
	ml_mov_b32 v53, 0x0
	ml_mov_b32 v54, 0x0
	ml_mov_b32 v55, 0x0
	ml_mov_b32 v48, 0x0
	ml_mov_b32 v49, 0x0
	ml_mov_b32 v50, 0x0
	ml_mov_b32 v51, 0x0
	ml_mov_b32 v44, 0x0
	ml_mov_b32 v45, 0x0
	ml_mov_b32 v46, 0x0
	ml_mov_b32 v47, 0x0
	ml_mov_b32 v40, 0x0
	ml_mov_b32 v41, 0x0
	ml_mov_b32 v42, 0x0
	ml_mov_b32 v43, 0x0
	ml_mov_b32 v36, 0x0
	ml_mov_b32 v37, 0x0
	ml_mov_b32 v38, 0x0
	ml_mov_b32 v39, 0x0
	ml_mov_b32 v32, 0x0
	ml_mov_b32 v33, 0x0
	ml_mov_b32 v34, 0x0
	ml_mov_b32 v35, 0x0
	ml_mov_b32 v28, 0x0
	ml_mov_b32 v29, 0x0
	ml_mov_b32 v30, 0x0
	ml_mov_b32 v31, 0x0
	ml_mov_b32 v24, 0x0
	ml_mov_b32 v25, 0x0
	ml_mov_b32 v26, 0x0
	ml_mov_b32 v27, 0x0
	ml_mov_b32 v20, 0x0
	ml_mov_b32 v21, 0x0
	ml_mov_b32 v22, 0x0
	ml_mov_b32 v23, 0x0
	ml_mov_b32 v16, 0x0
	ml_mov_b32 v17, 0x0
	ml_mov_b32 v18, 0x0
	ml_mov_b32 v19, 0x0
	ml_mov_b32 v12, 0x0
	ml_mov_b32 v13, 0x0
	ml_mov_b32 v14, 0x0
	ml_mov_b32 v15, 0x0
	ml_mov_b32 v8, 0x0
	ml_mov_b32 v9, 0x0
	ml_mov_b32 v10, 0x0
	ml_mov_b32 v11, 0x0
	ml_mov_b32 v4, 0x0
	ml_mov_b32 v5, 0x0
	ml_mov_b32 v6, 0x0
	ml_mov_b32 v7, 0x0
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v2, 0x0
	ml_mov_b32 v3, 0x0
BB0_1:                                  ; =>This Inner Loop Header: Depth=1
	sl_add_i32 s6, s19, 0x1
	sl_cmp_lt_i32 wcr, s6, 0x2
	sl_csel_b32 s19, s6, 0x0, wcr
	.loc	1 31 20                         ; candidate.py:31:20
	sl_wait g2scnt(0)
	sl_barrier_req 0x0
	sl_barrier_wait 0x0
	sl_mull_u32 s22, s19, 0x4000
	ml_slb_load_b32x1  v71, v65, s22, #0, null
	.loc	1 32 20                         ; candidate.py:32:20
	sl_add_i32 s23, s22, 0x8000
	sl_add_i32 s24, s22, 0x9000
	sl_add_i32 s25, s22, 0xa000
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v72, v65, s22, #256, null
	.loc	1 32 20                         ; candidate.py:32:20
	sl_add_i32 s26, s22, 0xb000
	.loc	1 31 20                         ; candidate.py:31:20
	sl_add_i32 s27, s22, 0x1000
	sl_add_i32 s28, s22, 0x2000
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v73, v66, s23, #0, null
	.loc	1 31 20                         ; candidate.py:31:20
	sl_add_i32 s29, s22, 0x3000
	.loc	1 30 19                         ; candidate.py:30:19
	sl_add_i32 s6, s13, 0x1
	sl_cmp_lt_i32 wcr, s6, 0x2
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v74, v67, s23, #0, null
	.loc	1 30 19                         ; candidate.py:30:19
	sl_csel_b32 s13, s6, 0x0, wcr
	.loc	1 31 20                         ; candidate.py:31:20
	sl_mull_u32 s6, s13, 0x4000
	sl_add_i32 s11, s15, s6
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v75, v66, s24, #0, null
	.loc	1 31 20                         ; candidate.py:31:20
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[10:11], 0x0, 0x0, 0x0, 0x1
	.loc	1 32 20                         ; candidate.py:32:20
	sl_mov_b64 s[6:7], s[2:3]
	sl_add_i32 s11, s11, 0x8000
	ml_slb_load_b32x1  v76, v67, s24, #0, null
	sl_sme_load_16x1b64_col s[4:7], s[10:11], 0x0, 0x0, 0x0, 0x1
	.loc	1 30 19                         ; candidate.py:30:19
	sl_add_i64 s[4:5], s[4:5], 0x40
	sl_add_i32 s18, s18, 0xffffffff
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v77, v66, s25, #0, null
	.loc	1 30 19                         ; candidate.py:30:19
	sl_cmp_eq_u32 wcr, s18, 0x0
	sl_add_i64 s[0:1], s[0:1], 0x40
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v78, v67, s25, #0, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[56:59], v[71:72], v[73:74], v[56:59]
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v79, v66, s26, #0, null
	ml_slb_load_b32x1  v80, v67, s26, #0, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[71:72], v[75:76], v[44:47]
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v81, v65, s27, #0, null
	ml_slb_load_b32x1  v82, v65, s27, #256, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[71:72], v[77:78], v[28:31]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[71:72], v[79:80], v[12:15]
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v71, v65, s28, #0, null
	ml_slb_load_b32x1  v72, v65, s28, #256, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[81:82], v[73:74], v[60:63]
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[81:82], v[75:76], v[40:43]
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[81:82], v[77:78], v[24:27]
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[81:82], v[79:80], v[8:11]
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v81, v65, s29, #0, null
	ml_slb_load_b32x1  v82, v65, s29, #256, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[52:55], v[71:72], v[73:74], v[52:55]
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[71:72], v[75:76], v[36:39]
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[71:72], v[77:78], v[20:23]
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[71:72], v[79:80], v[4:7]
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v71, v70, s22, #512, null
	ml_slb_load_b32x1  v72, v70, s22, #768, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[48:51], v[81:82], v[73:74], v[48:51]
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v73, v68, s23, #0, null
	ml_slb_load_b32x1  v74, v69, s23, #0, null
	.loc	1 34 25                         ; candidate.py:34:25
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[81:82], v[75:76], v[32:35]
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v75, v68, s24, #0, null
	ml_slb_load_b32x1  v76, v69, s24, #0, null
	.loc	1 34 25                         ; candidate.py:34:25
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[81:82], v[77:78], v[16:19]
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v77, v68, s25, #0, null
	ml_slb_load_b32x1  v78, v69, s25, #0, null
	.loc	1 34 25                         ; candidate.py:34:25
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[81:82], v[79:80], v[0:3]
	.loc	1 32 20                         ; candidate.py:32:20
	ml_slb_load_b32x1  v79, v68, s26, #0, null
	ml_slb_load_b32x1  v80, v69, s26, #0, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(6)
	ml_matrix_mad_f32_bf16_m16n16k16 v[56:59], v[71:72], v[73:74], v[56:59]
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v81, v70, s27, #512, null
	ml_slb_load_b32x1  v82, v70, s27, #768, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(6)
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[71:72], v[75:76], v[44:47]
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[71:72], v[77:78], v[28:31]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[71:72], v[79:80], v[12:15]
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v71, v70, s28, #512, null
	ml_slb_load_b32x1  v72, v70, s28, #768, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[81:82], v[73:74], v[60:63]
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[81:82], v[75:76], v[40:43]
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[81:82], v[77:78], v[24:27]
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[81:82], v[79:80], v[8:11]
	.loc	1 31 20                         ; candidate.py:31:20
	ml_slb_load_b32x1  v81, v70, s29, #512, null
	ml_slb_load_b32x1  v82, v70, s29, #768, null
	.loc	1 34 25                         ; candidate.py:34:25
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[52:55], v[71:72], v[73:74], v[52:55]
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[71:72], v[75:76], v[36:39]
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[71:72], v[77:78], v[20:23]
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[71:72], v[79:80], v[4:7]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[48:51], v[81:82], v[73:74], v[48:51]
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[81:82], v[75:76], v[32:35]
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[81:82], v[77:78], v[16:19]
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[81:82], v[79:80], v[0:3]
	.loc	1 30 19                         ; candidate.py:30:19
	sl_cbr_wcrz BB0_1, wcr
; %bb.2:
	.loc	1 20 32                         ; candidate.py:20:32
	ml_shl_b32 v68, v64, 0x1
	ml_and_b32 v65, v68, 0xe
	sl_srl_b32 {s0, wcr}, s17, 0x2
	.loc	1 21 19                         ; candidate.py:21:19
	sl_add_i32 s0, s16, s0
	ml_add_i32 v69, s0, v65
	ml_add_i32 v65, v69, 0xc0
	ml_add_i32 v66, v69, 0x80
	ml_add_i32 v67, v69, 0x40
	.loc	1 20 32                         ; candidate.py:20:32
	ml_bfe2_b32 v64, v64, 0x63
	sl_srl_b32 {s0, wcr}, s12, 0x4
	sl_and_b32 {s0, wcr}, s0, 0x30
	.loc	1 20 19 is_stmt 0               ; candidate.py:20:19
	sl_add_i32 s0, s14, s0
	ml_add_i32 v64, s0, v64
	ml_add_i32 v70, v64, 0xc8
	ml_add_i32 v71, v64, 0xc0
	ml_add_i32 v72, v64, 0x88
	ml_add_i32 v73, v64, 0x80
	ml_add_i32 v74, v64, 0x48
	ml_add_i32 v75, v64, 0x40
	ml_add_i32 v76, v64, 0x8
	.loc	1 30 19 is_stmt 1               ; candidate.py:30:19
	sl_wait g2scnt(0)
	sl_barrier 
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v77, v56
	ml_cvt_bf16_f32  v78, v57
	ml_cvt_bf16_f32  v79, v58
	ml_cvt_bf16_f32  v59, v59
	ml_cvt_bf16_f32  v60, v60
	ml_cvt_bf16_f32  v61, v61
	ml_cvt_bf16_f32  v62, v62
	ml_cvt_bf16_f32  v63, v63
	.loc	1 38 25                         ; candidate.py:38:25
	ml_cmp_lt_i32 tcr, v64, 0x7ee
	.loc	1 39 25                         ; candidate.py:39:25
	ml_shl_b32 v56, v64, 0xc
	ml_shl_b32 v57, v64, 0xb
	ml_add_i32 v58, v56, v57
	.loc	1 38 25                         ; candidate.py:38:25
	sl_mov_b64 s[16:17], tcr
	ml_cmp_lt_i32 tcr, v76, 0x7ee
	.loc	1 39 25                         ; candidate.py:39:25
	ml_shl_b32 v56, v76, 0xc
	ml_shl_b32 v57, v76, 0xb
	ml_add_i32 v57, v56, v57
	.loc	1 38 25                         ; candidate.py:38:25
	sl_mov_b64 s[12:13], tcr
	ml_cmp_lt_i32 tcr, v75, 0x7ee
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v56, v69, v58
	.loc	1 51 24                         ; candidate.py:51:24
	ml_sra_b32 v64, v56, 0x1f
	ml_shl_b32 v76, v56, 0x1
	.loc	1 38 25                         ; candidate.py:38:25
	sl_mov_b64 s[14:15], tcr
	ml_cmp_lt_i32 tcr, v74, 0x7ee
	.loc	1 51 24                         ; candidate.py:51:24
	ml_shl_b32 v64, v64, 0x1
	ml_srl_b32 v80, v56, 0x1f
	ml_or_b32 v64, v64, v80
	.loc	1 38 25                         ; candidate.py:38:25
	sl_mov_b64 s[10:11], tcr
	ml_cmp_lt_i32 tcr, v73, 0x7ee
	.loc	1 51 24                         ; candidate.py:51:24
	ml_mov_b32 v80, s21
	.loc	1 37 23                         ; candidate.py:37:23
	sl_mov_b32 s18, 0x1000504
	ml_byte_permute_b32 v77, v78, v77, s18
	.loc	1 38 25                         ; candidate.py:38:25
	sl_mov_b64 s[4:5], tcr
	ml_cmp_lt_i32 tcr, v72, 0x7ee
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v59, v59, v79, s18
	ml_byte_permute_b32 v60, v61, v60, s18
	ml_byte_permute_b32 v61, v63, v62, s18
	.loc	1 38 25                         ; candidate.py:38:25
	sl_mov_b64 s[6:7], tcr
	ml_cmp_lt_i32 tcr, v71, 0x7ee
	.loc	1 37 23                         ; candidate.py:37:23
	ml_and_b32 v62, tid, 0x1
	ml_mov_b32 v63, 0x5410
	sl_mov_b32 s19, 0x2010200
	.loc	1 38 25                         ; candidate.py:38:25
	sl_mov_b64 s[0:1], tcr
	ml_cmp_lt_i32 tcr, v70, 0x7ee
	.loc	1 37 23                         ; candidate.py:37:23
	ml_and_b32 v81, tid, 0x20
	sl_mov_b32 s23, 0xffffffff
	.loc	1 38 25                         ; candidate.py:38:25
	sl_mov_b64 s[2:3], tcr
	.loc	1 51 24                         ; candidate.py:51:24
	ml_addo_u32 {v76, tcr}, s20, v76
	.loc	1 51 41 is_stmt 0               ; candidate.py:51:41
	ml_mov_v2s_b32 s20, v76, 0x0
	.loc	1 51 24                         ; candidate.py:51:24
	ml_addc_i32 v64, v80, v64, tcr
	.loc	1 37 23 is_stmt 1               ; candidate.py:37:23
	ml_cmp_eq_u32 tcr, v62, 0x0
	ml_mov_b32 v62, 0x7632
	ml_csel_b32 v78, v63, v62, tcr
	ml_csel_b32 v79, v62, v63, tcr
	ml_byte_permute_b32 v78, v78, v78, s19
	ml_pk_shl_b16 v78, v78, 0x40004
	ml_pk_srl_b8 v78, v78, 0x40004
	ml_byte_permute_b32 v80, v77, v59, v78
	ml_byte_permute_b32 v79, v79, v79, s19
	ml_pk_shl_b16 v79, v79, 0x40004
	ml_pk_srl_b8 v79, v79, 0x40004
	ml_byte_permute_b32 v59, v77, v59, v79
	ml_bfe2_b32 v77, tid, 0x25
	ml_anyop3_b32 v68, 62, v68, v77, 0xfffffff8
	ml_slb_shuffle_rtn_b32 v77, v80, v68
	ml_byte_permute_b32 v80, v60, v61, v78
	ml_byte_permute_b32 v60, v60, v61, v79
	ml_xor_b32 v61, v68, 0x1
	ml_slb_shuffle_rtn_b32 v59, v59, v61
	ml_cmp_eq_u32 tcr, v81, 0x0
	ml_mov_b32 v81, 0x1054
	ml_csel_b32 v63, v63, v81, tcr
	ml_byte_permute_b32 v63, v63, v63, s19
	ml_pk_shl_b16 v63, v63, 0x40004
	ml_pk_srl_b8 v63, v63, 0x40004
	.loc	1 51 41                         ; candidate.py:51:41
	ml_mov_v2s_b32 s21, v64, 0x0
	ml_mov_b32 v64, s20
	ml_sub_i32 v64, v76, v64
	.loc	1 37 23                         ; candidate.py:37:23
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v76, v77, v59, v63
	.loc	1 51 41                         ; candidate.py:51:41
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[16:17], tmsk
	ml_lsa_store_dword v76, s[20:23], signed v64, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	ml_mov_b32 v76, 0x3276
	.loc	1 37 23                         ; candidate.py:37:23
	ml_csel_b32 v62, v62, v76, tcr
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v76, v69, v57
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v80, v80, v68
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v76, v76, v56
	ml_shl_b32 v76, v76, 0x1
	ml_mov_v2s_b32 s22, v76, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v52, v52
	ml_slb_shuffle_rtn_b32 v60, v60, v61
	ml_byte_permute_b32 v62, v62, v62, s19
	ml_pk_shl_b16 v62, v62, 0x40004
	ml_pk_srl_b8 v62, v62, 0x40004
	ml_byte_permute_b32 v59, v77, v59, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v76, s22, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[12:13], tmsk
	ml_lsa_store_dword v59, s[20:23], signed v76, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v53, v53
	.loc	1 39 25                         ; candidate.py:39:25
	ml_shl_b32 v59, v75, 0xc
	ml_shl_b32 v75, v75, 0xb
	ml_add_i32 v59, v59, v75
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v75, v69, v59
	.loc	1 51 41 is_stmt 1               ; candidate.py:51:41
	ml_sub_i32 v75, v75, v56
	ml_shl_b32 v75, v75, 0x1
	ml_mov_v2s_b32 s19, v75, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v54, v54
	ml_cvt_bf16_f32  v55, v55
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v75, v80, v60, v63
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v76, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[14:15], tmsk
	ml_lsa_store_dword v75, s[20:23], signed v76, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 39 25                         ; candidate.py:39:25
	ml_shl_b32 v75, v74, 0xc
	ml_shl_b32 v74, v74, 0xb
	ml_add_i32 v74, v75, v74
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v52, v53, v52, s18
	ml_byte_permute_b32 v53, v55, v54, s18
	ml_byte_permute_b32 v54, v52, v53, v78
	ml_byte_permute_b32 v52, v52, v53, v79
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v53, v69, v74
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v54, v54, v68
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v53, v53, v56
	ml_shl_b32 v53, v53, 0x1
	ml_mov_v2s_b32 s19, v53, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v52, v52, v61
	ml_cvt_bf16_f32  v48, v48
	ml_byte_permute_b32 v53, v80, v60, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v55, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[10:11], tmsk
	ml_lsa_store_dword v53, s[20:23], signed v55, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v49, v49
	.loc	1 39 25                         ; candidate.py:39:25
	ml_shl_b32 v53, v73, 0xc
	ml_shl_b32 v55, v73, 0xb
	ml_add_i32 v53, v53, v55
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v55, v69, v53
	.loc	1 51 41 is_stmt 1               ; candidate.py:51:41
	ml_sub_i32 v55, v55, v56
	ml_shl_b32 v55, v55, 0x1
	ml_mov_v2s_b32 s19, v55, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v50, v50
	ml_cvt_bf16_f32  v51, v51
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v55, v54, v52, v63
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v60, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v55, s[20:23], signed v60, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 39 25                         ; candidate.py:39:25
	ml_shl_b32 v55, v72, 0xc
	ml_shl_b32 v60, v72, 0xb
	ml_add_i32 v55, v55, v60
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v48, v49, v48, s18
	ml_byte_permute_b32 v49, v51, v50, s18
	ml_byte_permute_b32 v50, v48, v49, v78
	ml_byte_permute_b32 v48, v48, v49, v79
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v49, v69, v55
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v50, v50, v68
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v49, v49, v56
	ml_shl_b32 v49, v49, 0x1
	ml_mov_v2s_b32 s19, v49, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v48, v48, v61
	ml_cvt_bf16_f32  v44, v44
	ml_byte_permute_b32 v49, v54, v52, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v51, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v49, s[20:23], signed v51, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v45, v45
	.loc	1 39 25                         ; candidate.py:39:25
	ml_shl_b32 v49, v71, 0xc
	ml_shl_b32 v51, v71, 0xb
	ml_add_i32 v49, v49, v51
	.loc	1 39 32 is_stmt 0               ; candidate.py:39:32
	ml_add_i32 v51, v69, v49
	.loc	1 51 41 is_stmt 1               ; candidate.py:51:41
	ml_sub_i32 v51, v51, v56
	ml_shl_b32 v51, v51, 0x1
	ml_mov_v2s_b32 s19, v51, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v46, v46
	ml_cvt_bf16_f32  v47, v47
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v51, v50, v48, v63
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v52, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v51, s[20:23], signed v52, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 39 25                         ; candidate.py:39:25
	ml_shl_b32 v51, v70, 0xc
	ml_shl_b32 v52, v70, 0xb
	ml_add_i32 v51, v51, v52
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v44, v45, v44, s18
	ml_byte_permute_b32 v45, v47, v46, s18
	ml_byte_permute_b32 v46, v44, v45, v78
	ml_byte_permute_b32 v44, v44, v45, v79
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v45, v69, v51
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v46, v46, v68
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v45, v45, v56
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s19, v45, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v44, v44, v61
	ml_cvt_bf16_f32  v40, v40
	ml_byte_permute_b32 v45, v50, v48, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v47, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[2:3], tmsk
	ml_lsa_store_dword v45, s[20:23], signed v47, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v41, v41
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v45, v67, v58
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v45, v45, v56
	ml_shl_b32 v45, v45, 0x1
	ml_mov_v2s_b32 s19, v45, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v42, v42
	ml_cvt_bf16_f32  v43, v43
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v45, v46, v44, v63
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v47, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[16:17], tmsk
	ml_lsa_store_dword v45, s[20:23], signed v47, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v40, v41, v40, s18
	ml_byte_permute_b32 v41, v43, v42, s18
	ml_byte_permute_b32 v42, v40, v41, v78
	ml_byte_permute_b32 v40, v40, v41, v79
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v41, v67, v57
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v42, v42, v68
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v41, v41, v56
	ml_shl_b32 v41, v41, 0x1
	ml_mov_v2s_b32 s19, v41, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v40, v40, v61
	ml_cvt_bf16_f32  v36, v36
	ml_byte_permute_b32 v41, v46, v44, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v43, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[12:13], tmsk
	ml_lsa_store_dword v41, s[20:23], signed v43, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v37, v37
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v41, v67, v59
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v41, v41, v56
	ml_shl_b32 v41, v41, 0x1
	ml_mov_v2s_b32 s19, v41, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v38, v38
	ml_cvt_bf16_f32  v39, v39
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v41, v42, v40, v63
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v43, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[14:15], tmsk
	ml_lsa_store_dword v41, s[20:23], signed v43, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v36, v37, v36, s18
	ml_byte_permute_b32 v37, v39, v38, s18
	ml_byte_permute_b32 v38, v36, v37, v78
	ml_byte_permute_b32 v36, v36, v37, v79
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v37, v67, v74
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v38, v38, v68
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v37, v37, v56
	ml_shl_b32 v37, v37, 0x1
	ml_mov_v2s_b32 s19, v37, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v36, v36, v61
	ml_cvt_bf16_f32  v32, v32
	ml_byte_permute_b32 v37, v42, v40, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v39, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[10:11], tmsk
	ml_lsa_store_dword v37, s[20:23], signed v39, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v33, v33
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v37, v67, v53
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v37, v37, v56
	ml_shl_b32 v37, v37, 0x1
	ml_mov_v2s_b32 s19, v37, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v34, v34
	ml_cvt_bf16_f32  v35, v35
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v37, v38, v36, v63
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v39, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v37, s[20:23], signed v39, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v32, v33, v32, s18
	ml_byte_permute_b32 v33, v35, v34, s18
	ml_byte_permute_b32 v34, v32, v33, v78
	ml_byte_permute_b32 v32, v32, v33, v79
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v33, v67, v55
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v34, v34, v68
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v33, v33, v56
	ml_shl_b32 v33, v33, 0x1
	ml_mov_v2s_b32 s19, v33, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v32, v32, v61
	ml_cvt_bf16_f32  v28, v28
	ml_byte_permute_b32 v33, v38, v36, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v35, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v33, s[20:23], signed v35, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v29, v29
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v33, v67, v49
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v33, v33, v56
	ml_shl_b32 v33, v33, 0x1
	ml_mov_v2s_b32 s19, v33, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v30, v30
	ml_cvt_bf16_f32  v31, v31
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v33, v34, v32, v63
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v35, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v33, s[20:23], signed v35, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v28, v29, v28, s18
	ml_byte_permute_b32 v29, v31, v30, s18
	ml_byte_permute_b32 v30, v28, v29, v78
	ml_byte_permute_b32 v28, v28, v29, v79
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v29, v67, v51
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v30, v30, v68
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v29, v29, v56
	ml_shl_b32 v29, v29, 0x1
	ml_mov_v2s_b32 s19, v29, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v28, v28, v61
	ml_cvt_bf16_f32  v24, v24
	ml_byte_permute_b32 v29, v34, v32, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v31, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[2:3], tmsk
	ml_lsa_store_dword v29, s[20:23], signed v31, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v25, v25
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v29, v66, v58
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v29, v29, v56
	ml_shl_b32 v29, v29, 0x1
	ml_mov_v2s_b32 s19, v29, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v26, v26
	ml_cvt_bf16_f32  v27, v27
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v29, v30, v28, v63
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v31, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[16:17], tmsk
	ml_lsa_store_dword v29, s[20:23], signed v31, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v24, v25, v24, s18
	ml_byte_permute_b32 v25, v27, v26, s18
	ml_byte_permute_b32 v26, v24, v25, v78
	ml_byte_permute_b32 v24, v24, v25, v79
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v25, v66, v57
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v26, v26, v68
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v25, v25, v56
	ml_shl_b32 v25, v25, 0x1
	ml_mov_v2s_b32 s19, v25, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v24, v24, v61
	ml_cvt_bf16_f32  v20, v20
	ml_byte_permute_b32 v25, v30, v28, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v27, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[12:13], tmsk
	ml_lsa_store_dword v25, s[20:23], signed v27, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v21, v21
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v25, v66, v59
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v25, v25, v56
	ml_shl_b32 v25, v25, 0x1
	ml_mov_v2s_b32 s19, v25, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v22, v22
	ml_cvt_bf16_f32  v23, v23
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v25, v26, v24, v63
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v27, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[14:15], tmsk
	ml_lsa_store_dword v25, s[20:23], signed v27, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v20, v21, v20, s18
	ml_byte_permute_b32 v21, v23, v22, s18
	ml_byte_permute_b32 v22, v20, v21, v78
	ml_byte_permute_b32 v20, v20, v21, v79
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v21, v66, v74
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v22, v22, v68
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v21, v21, v56
	ml_shl_b32 v21, v21, 0x1
	ml_mov_v2s_b32 s19, v21, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v20, v20, v61
	ml_cvt_bf16_f32  v16, v16
	ml_byte_permute_b32 v21, v26, v24, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v23, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[10:11], tmsk
	ml_lsa_store_dword v21, s[20:23], signed v23, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v17, v17
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v21, v66, v53
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v21, v21, v56
	ml_shl_b32 v21, v21, 0x1
	ml_mov_v2s_b32 s19, v21, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v18, v18
	ml_cvt_bf16_f32  v19, v19
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v21, v22, v20, v63
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v23, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v21, s[20:23], signed v23, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v16, v17, v16, s18
	ml_byte_permute_b32 v17, v19, v18, s18
	ml_byte_permute_b32 v18, v16, v17, v78
	ml_byte_permute_b32 v16, v16, v17, v79
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v17, v66, v55
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v18, v18, v68
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v17, v17, v56
	ml_shl_b32 v17, v17, 0x1
	ml_mov_v2s_b32 s19, v17, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v16, v16, v61
	ml_cvt_bf16_f32  v12, v12
	ml_byte_permute_b32 v17, v22, v20, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v19, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v17, s[20:23], signed v19, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v13, v13
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v17, v66, v49
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v17, v17, v56
	ml_shl_b32 v17, v17, 0x1
	ml_mov_v2s_b32 s19, v17, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v14, v14
	ml_cvt_bf16_f32  v15, v15
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v17, v18, v16, v63
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v19, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v17, s[20:23], signed v19, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v12, v13, v12, s18
	ml_byte_permute_b32 v13, v15, v14, s18
	ml_byte_permute_b32 v14, v12, v13, v78
	ml_byte_permute_b32 v12, v12, v13, v79
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v13, v66, v51
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v14, v14, v68
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v13, v13, v56
	ml_shl_b32 v13, v13, 0x1
	ml_mov_v2s_b32 s19, v13, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v12, v12, v61
	ml_byte_permute_b32 v13, v18, v16, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v15, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[2:3], tmsk
	ml_lsa_store_dword v13, s[20:23], signed v15, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v8, v8
	ml_cvt_bf16_f32  v9, v9
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v13, v65, v58
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v13, v13, v56
	ml_shl_b32 v13, v13, 0x1
	ml_mov_v2s_b32 s19, v13, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v10, v10
	ml_cvt_bf16_f32  v11, v11
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v13, v14, v12, v63
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v15, s19, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[16:17], tmsk
	ml_lsa_store_dword v13, s[20:23], signed v15, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v8, v9, v8, s18
	ml_byte_permute_b32 v9, v11, v10, s18
	ml_byte_permute_b32 v10, v8, v9, v78
	ml_slb_shuffle_rtn_b32 v10, v10, v68
	ml_byte_permute_b32 v8, v8, v9, v79
	ml_byte_permute_b32 v9, v14, v12, v62
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v11, v65, v57
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v8, v8, v61
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v11, v11, v56
	ml_shl_b32 v11, v11, 0x1
	ml_mov_v2s_b32 s16, v11, 0x0
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v11, v65, v59
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v11, v11, v56
	ml_shl_b32 v11, v11, 0x1
	ml_mov_v2s_b32 s17, v11, 0x0
	ml_add_i32 v11, s16, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[12:13], tmsk
	ml_lsa_store_dword v9, s[20:23], signed v11, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v9, v10, v8, v63
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v11, s17, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[14:15], tmsk
	ml_lsa_store_dword v9, s[20:23], signed v11, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v4, v4
	ml_cvt_bf16_f32  v5, v5
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v9, v65, v74
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v9, v9, v56
	ml_shl_b32 v9, v9, 0x1
	ml_mov_v2s_b32 s12, v9, 0x0
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v6, v6
	ml_cvt_bf16_f32  v7, v7
	ml_byte_permute_b32 v8, v10, v8, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v9, s12, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[10:11], tmsk
	ml_lsa_store_dword v8, s[20:23], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_cvt_bf16_f32  v0, v0
	ml_cvt_bf16_f32  v1, v1
	ml_byte_permute_b32 v4, v5, v4, s18
	ml_byte_permute_b32 v5, v7, v6, s18
	ml_byte_permute_b32 v6, v4, v5, v78
	ml_slb_shuffle_rtn_b32 v6, v6, v68
	ml_cvt_bf16_f32  v2, v2
	ml_cvt_bf16_f32  v3, v3
	ml_byte_permute_b32 v4, v4, v5, v79
	ml_slb_shuffle_rtn_b32 v4, v4, v61
	ml_byte_permute_b32 v0, v1, v0, s18
	ml_byte_permute_b32 v1, v3, v2, s18
	ml_byte_permute_b32 v2, v0, v1, v78
	ml_slb_shuffle_rtn_b32 v2, v2, v68
	ml_byte_permute_b32 v0, v0, v1, v79
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v1, v65, v53
	ml_add_i32 v3, v65, v55
	.loc	1 37 23                         ; candidate.py:37:23
	ml_slb_shuffle_rtn_b32 v0, v0, v61
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v1, v1, v56
	ml_shl_b32 v1, v1, 0x1
	ml_mov_v2s_b32 s10, v1, 0x0
	ml_sub_i32 v3, v3, v56
	ml_shl_b32 v3, v3, 0x1
	ml_mov_v2s_b32 s11, v3, 0x0
	ml_add_i32 v3, s10, v64
	.loc	1 37 23                         ; candidate.py:37:23
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v1, v6, v4, v63
	.loc	1 51 41                         ; candidate.py:51:41
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v1, s[20:23], signed v3, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v1, v6, v4, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v3, s11, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v1, s[20:23], signed v3, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 39 32                         ; candidate.py:39:32
	ml_add_i32 v1, v65, v49
	ml_add_i32 v3, v65, v51
	.loc	1 51 41                         ; candidate.py:51:41
	ml_sub_i32 v1, v1, v56
	ml_shl_b32 v1, v1, 0x1
	ml_mov_v2s_b32 s4, v1, 0x0
	ml_sub_i32 v1, v3, v56
	.loc	1 37 23                         ; candidate.py:37:23
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v3, v2, v0, v63
	.loc	1 51 41                         ; candidate.py:51:41
	ml_shl_b32 v1, v1, 0x1
	ml_mov_v2s_b32 s5, v1, 0x0
	ml_add_i32 v1, s4, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v3, s[20:23], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 37 23                         ; candidate.py:37:23
	ml_byte_permute_b32 v0, v2, v0, v62
	.loc	1 51 41                         ; candidate.py:51:41
	ml_add_i32 v1, s5, v64
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[2:3], tmsk
	ml_lsa_store_dword v0, s[20:23], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 40 4                          ; candidate.py:40:4
	sl_eop 
.Ltmp1:
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
	.long	536852
	.asciz	"\003\000\224\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	half_mm, .Lfunc_end0-half_mm
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 6880
; NumSgprs: 36
; NumVgprs: 83
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 4
; VGPRBlocks: 20
; NumSGPRsForWarpsPerNU: 32
; NumVGPRsForWarpsPerNR: 83
; ReqNTIDx: 0
; MaxNTIDx: 0
; MinCTASm: 0
; ActiveWarp: 3
; WarpLimiterHint : 0
	.section	.debug_abbrev,"",@progbits
	.byte	1                               ; Abbreviation Code
	.byte	17                              ; DW_TAG_compile_unit
	.byte	0                               ; DW_CHILDREN_no
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
	.byte	0                               ; EOM(3)
	.section	.debug_info,"",@progbits
	.long	161                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0x9a DW_TAG_compile_unit
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
    .sgpr_count:     36
    .sgpr_spill_count: 0
    .symbol:         half_mm.kd
    .vgpr_count:     83
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
