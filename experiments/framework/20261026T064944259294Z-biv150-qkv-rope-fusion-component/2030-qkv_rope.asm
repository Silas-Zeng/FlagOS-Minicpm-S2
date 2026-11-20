	.text
	.globl	qkv_rope                        ; -- Begin function qkv_rope
	.p2align	3
	.type	qkv_rope,@function
	.iluvatar_kernel qkv_rope
qkv_rope:                               ; @qkv_rope
.Lfunc_begin0:
	.file	1 "/workspace/experiments/minicpm-s2/framework/20261026T064944259294Z-biv150-qkv-rope-fusion-component/source" "candidate.py"
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
		granulated_workitem_vgpr_count = 60
		granulated_warp_sgpr_count = 12
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
		kernarg_segment_byte_size = 72
		workgroup_fbarrier_count = 0
		warp_sgpr_count = 99
		workitem_vgpr_count = 244
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
	sl_mov_b32 s44, tcr_lo
	ml_vrf_init_u32 v64, tcr
.Ltmp0:
	.loc	1 10 22 prologue_end            ; candidate.py:10:22
	sl_lsa_load_b32x16 s[20:35], s[4:5], noreg, #0, ca
	.loc	1 11 12                         ; candidate.py:11:12
	sl_mulh_u32 s0, s6, 0x66666667
	sl_srl_b32 {s4, wcr}, s0, 0x3
	.loc	1 12 12                         ; candidate.py:12:12
	sl_mull_u32 s16, s4, 0x100
	.loc	1 12 27 is_stmt 0               ; candidate.py:12:27
	sl_bfe2_b32 s17, tcr_lo, 0x66
	.loc	1 15 12 is_stmt 1               ; candidate.py:15:12
	sl_mulh_i32 s0, s16, 0x81228dbf
	sl_add_i32 s0, s0, s16
	sl_srl_b32 {s1, wcr}, s0, 0x1f
	sl_srl_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s1
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s0, s16, s0
	.loc	1 16 20                         ; candidate.py:16:20
	sl_mull_u32 s0, s0, 0x800
	.loc	1 16 9 is_stmt 0                ; candidate.py:16:9
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_wait smcnt(0)
	sl_add_i64 s[0:1], s[20:21], s[0:1]
	sl_mov_b32 s3, 0x1000
	sl_mov_b32 s2, 0xffffffff
	.loc	1 20 18 is_stmt 1               ; candidate.py:20:18
	sl_mull_u32 s10, s17, 0x10000
	sl_mull_u32 s18, s17, 0x400
	sl_mov_b32 s11, s18
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[10:11], 0x0, 0x0, 0x0, 0x1
	sl_add_i32 s12, s10, 0x80000
	sl_mov_b32 s13, s18
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[12:13], 0x0, 0x0, 0x800, 0x1
	.loc	1 11 22                         ; candidate.py:11:22
	sl_mull_u32 s4, s4, 0xffffffec
	sl_add_i32 s43, s4, s6
	.loc	1 17 22                         ; candidate.py:17:22
	sl_mull_u32 s14, s43, 0x40000
	.loc	1 17 9 is_stmt 0                ; candidate.py:17:9
	sl_mov_b32 s15, 0x0
	sl_shl_b64 {s[4:5], wcr}, s[14:15], 0x1
	ml_mov_s2v_b32 v242, s20, 0x0
	ml_mov_s2v_b32 v242, s21, 0x1
	ml_mov_s2v_b32 v242, s22, 0x2
	ml_mov_s2v_b32 v242, s23, 0x3
	ml_mov_s2v_b32 v242, s24, 0x4
	ml_mov_s2v_b32 v242, s25, 0x5
	ml_mov_s2v_b32 v242, s26, 0x6
	ml_mov_s2v_b32 v242, s27, 0x7
	ml_mov_s2v_b32 v242, s28, 0x8
	ml_mov_s2v_b32 v242, s29, 0x9
	ml_mov_s2v_b32 v242, s30, 0xa
	ml_mov_s2v_b32 v242, s31, 0xb
	ml_mov_s2v_b32 v242, s32, 0xc
	ml_mov_s2v_b32 v242, s33, 0xd
	ml_mov_s2v_b32 v242, s34, 0xe
	ml_mov_s2v_b32 v242, s35, 0xf
	sl_add_i64 s[4:5], s[22:23], s[4:5]
	.loc	1 20 32 is_stmt 1               ; candidate.py:20:32
	sl_mov_b64 s[6:7], s[2:3]
	sl_add_i32 s11, s18, 0x8000
	sl_sme_load_16x1b64_col s[4:7], s[10:11], 0x0, 0x0, 0x0, 0x1
	ml_shl_b32 v70, v64, 0x3
	ml_mov_v2s_b32 s6, v70, 0x0
	ml_shl_b32 v0, tid, 0x2
	ml_shl_b32 v65, v64, 0x4
	ml_shl_b32 v2, v64, 0x6
	sl_and_b32 {s14, wcr}, s6, 0xc00
	ml_mov_v2s_b32 s6, v65, 0x0
	ml_add_i32 v1, s14, v0
	ml_and_b32 v2, v2, 0x300
	.loc	1 19 23                         ; candidate.py:19:23
	sl_add_i64 s[4:5], s[4:5], 0x40
	sl_and_b32 {s6, wcr}, s6, 0x400
	ml_anyop3_b32 v66, s6, v2, v0, 0xfffffffe
	ml_xor_b32 v67, v66, 0x10
	ml_xor_b32 v68, v66, 0x20
	ml_xor_b32 v69, v66, 0x30
	sl_add_i64 s[0:1], s[0:1], 0x40
	sl_mov_b32 s19, 0x40
	ml_mov_b32 v0, 0x0
	ml_xor_b32 v71, v1, 0x80
	sl_mov_b32 s20, s2
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v2, 0x0
	ml_mov_b32 v3, 0x0
	ml_mov_b32 v16, 0x0
	ml_mov_b32 v17, 0x0
	ml_mov_b32 v18, 0x0
	ml_mov_b32 v19, 0x0
	ml_mov_b32 v32, 0x0
	ml_mov_b32 v33, 0x0
	ml_mov_b32 v34, 0x0
	ml_mov_b32 v35, 0x0
	ml_mov_b32 v48, 0x0
	ml_mov_b32 v49, 0x0
	ml_mov_b32 v50, 0x0
	ml_mov_b32 v51, 0x0
	ml_mov_b32 v4, 0x0
	ml_mov_b32 v5, 0x0
	ml_mov_b32 v6, 0x0
	ml_mov_b32 v7, 0x0
	ml_mov_b32 v20, 0x0
	ml_mov_b32 v21, 0x0
	ml_mov_b32 v22, 0x0
	ml_mov_b32 v23, 0x0
	ml_mov_b32 v36, 0x0
	ml_mov_b32 v37, 0x0
	ml_mov_b32 v38, 0x0
	ml_mov_b32 v39, 0x0
	ml_mov_b32 v52, 0x0
	ml_mov_b32 v53, 0x0
	ml_mov_b32 v54, 0x0
	ml_mov_b32 v55, 0x0
	ml_mov_b32 v8, 0x0
	ml_mov_b32 v9, 0x0
	ml_mov_b32 v10, 0x0
	ml_mov_b32 v11, 0x0
	ml_mov_b32 v24, 0x0
	ml_mov_b32 v25, 0x0
	ml_mov_b32 v26, 0x0
	ml_mov_b32 v27, 0x0
	ml_mov_b32 v40, 0x0
	ml_mov_b32 v41, 0x0
	ml_mov_b32 v42, 0x0
	ml_mov_b32 v43, 0x0
	ml_mov_b32 v56, 0x0
	ml_mov_b32 v57, 0x0
	ml_mov_b32 v58, 0x0
	ml_mov_b32 v59, 0x0
	ml_mov_b32 v12, 0x0
	ml_mov_b32 v13, 0x0
	ml_mov_b32 v14, 0x0
	ml_mov_b32 v15, 0x0
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
BB0_1:                                  ; =>This Inner Loop Header: Depth=1
	sl_add_i32 s6, s20, 0x1
	sl_cmp_lt_i32 wcr, s6, 0x2
	sl_csel_b32 s20, s6, 0x0, wcr
	.loc	1 20 18                         ; candidate.py:20:18
	sl_wait g2scnt(0)
	sl_barrier_req 0x0
	sl_barrier_wait 0x0
	sl_mull_u32 s21, s20, 0x4000
	sl_add_i32 s22, s14, s21
	ml_slb_blkload_x1  v72, noreg, s22, #0, null
	.loc	1 20 32 is_stmt 0               ; candidate.py:20:32
	sl_mull_u32 s6, s20, 0x2000
	sl_add_i32 s23, s6, 0x8000
	sl_add_i32 s34, s6, 0x8800
	.loc	1 20 18                         ; candidate.py:20:18
	ml_slb_blkload_x1  v73, noreg, s22, #256, null
	.loc	1 20 32                         ; candidate.py:20:32
	sl_add_i32 s35, s6, 0x9000
	sl_add_i32 s36, s6, 0x9800
	.loc	1 20 18                         ; candidate.py:20:18
	sl_add_i32 s37, s21, 0x1000
	.loc	1 20 32                         ; candidate.py:20:32
	ml_slb_load_b32x1  v74, v66, s23, #0, null
	.loc	1 20 18                         ; candidate.py:20:18
	sl_add_i32 s38, s14, s37
	sl_add_i32 s39, s21, 0x2000
	sl_add_i32 s40, s14, s39
	.loc	1 20 32                         ; candidate.py:20:32
	ml_slb_load_b32x1  v75, v67, s23, #0, null
	.loc	1 20 18                         ; candidate.py:20:18
	sl_add_i32 s41, s21, 0x3000
	sl_add_i32 s42, s14, s41
	.loc	1 19 23 is_stmt 1               ; candidate.py:19:23
	sl_add_i32 s6, s15, 0x1
	.loc	1 20 32                         ; candidate.py:20:32
	ml_slb_load_b32x1  v76, v66, s34, #0, null
	.loc	1 19 23                         ; candidate.py:19:23
	sl_cmp_lt_i32 wcr, s6, 0x2
	sl_csel_b32 s15, s6, 0x0, wcr
	.loc	1 20 18                         ; candidate.py:20:18
	sl_mull_u32 s6, s15, 0x4000
	.loc	1 20 32 is_stmt 0               ; candidate.py:20:32
	ml_slb_load_b32x1  v77, v67, s34, #0, null
	.loc	1 20 18                         ; candidate.py:20:18
	sl_add_i32 s11, s18, s6
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[10:11], 0x0, 0x0, 0x0, 0x1
	sl_mov_b32 s13, s11
	.loc	1 20 32                         ; candidate.py:20:32
	ml_slb_load_b32x1  v78, v66, s35, #0, null
	.loc	1 20 18                         ; candidate.py:20:18
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[12:13], 0x0, 0x0, 0x800, 0x1
	.loc	1 20 32                         ; candidate.py:20:32
	sl_mull_u32 s11, s15, 0x2000
	sl_mov_b64 s[6:7], s[2:3]
	ml_slb_load_b32x1  v79, v67, s35, #0, null
	sl_add_i32 s11, s18, s11
	sl_add_i32 s11, s11, 0x8000
	sl_sme_load_16x1b64_col s[4:7], s[10:11], 0x0, 0x0, 0x0, 0x1
	.loc	1 21 23 is_stmt 1               ; candidate.py:21:23
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[72:73], v[74:75], v[0:3]
	.loc	1 19 23                         ; candidate.py:19:23
	sl_add_i64 s[4:5], s[4:5], 0x40
	.loc	1 20 32                         ; candidate.py:20:32
	ml_slb_load_b32x1  v80, v66, s36, #0, null
	.loc	1 19 23                         ; candidate.py:19:23
	sl_add_i32 s19, s19, 0xffffffff
	sl_cmp_eq_u32 wcr, s19, 0x0
	sl_add_i64 s[0:1], s[0:1], 0x40
	.loc	1 20 32                         ; candidate.py:20:32
	ml_slb_load_b32x1  v81, v67, s36, #0, null
	.loc	1 21 23                         ; candidate.py:21:23
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[72:73], v[76:77], v[4:7]
	.loc	1 20 18                         ; candidate.py:20:18
	ml_slb_blkload_x1  v82, noreg, s38, #0, null
	ml_slb_blkload_x1  v83, noreg, s38, #256, null
	.loc	1 21 23                         ; candidate.py:21:23
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[72:73], v[78:79], v[8:11]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[72:73], v[80:81], v[12:15]
	.loc	1 20 18                         ; candidate.py:20:18
	ml_slb_blkload_x1  v72, noreg, s40, #0, null
	ml_slb_blkload_x1  v73, noreg, s40, #256, null
	.loc	1 21 23                         ; candidate.py:21:23
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[82:83], v[74:75], v[16:19]
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[82:83], v[76:77], v[20:23]
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[82:83], v[78:79], v[24:27]
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[82:83], v[80:81], v[28:31]
	.loc	1 20 18                         ; candidate.py:20:18
	ml_slb_blkload_x1  v82, noreg, s42, #0, null
	ml_slb_blkload_x1  v83, noreg, s42, #256, null
	.loc	1 21 23                         ; candidate.py:21:23
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[72:73], v[74:75], v[32:35]
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[72:73], v[76:77], v[36:39]
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[72:73], v[78:79], v[40:43]
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[72:73], v[80:81], v[44:47]
	.loc	1 20 18                         ; candidate.py:20:18
	ml_slb_load_b32x1  v72, v71, s21, #512, null
	ml_slb_load_b32x1  v73, v71, s21, #768, null
	.loc	1 21 23                         ; candidate.py:21:23
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[48:51], v[82:83], v[74:75], v[48:51]
	.loc	1 20 32                         ; candidate.py:20:32
	ml_slb_load_b32x1  v74, v68, s23, #0, null
	ml_slb_load_b32x1  v75, v69, s23, #0, null
	.loc	1 21 23                         ; candidate.py:21:23
	ml_matrix_mad_f32_bf16_m16n16k16 v[52:55], v[82:83], v[76:77], v[52:55]
	.loc	1 20 32                         ; candidate.py:20:32
	ml_slb_load_b32x1  v76, v68, s34, #0, null
	ml_slb_load_b32x1  v77, v69, s34, #0, null
	.loc	1 21 23                         ; candidate.py:21:23
	ml_matrix_mad_f32_bf16_m16n16k16 v[56:59], v[82:83], v[78:79], v[56:59]
	.loc	1 20 32                         ; candidate.py:20:32
	ml_slb_load_b32x1  v78, v68, s35, #0, null
	ml_slb_load_b32x1  v79, v69, s35, #0, null
	.loc	1 21 23                         ; candidate.py:21:23
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[82:83], v[80:81], v[60:63]
	.loc	1 20 32                         ; candidate.py:20:32
	ml_slb_load_b32x1  v80, v68, s36, #0, null
	ml_slb_load_b32x1  v81, v69, s36, #0, null
	.loc	1 21 23                         ; candidate.py:21:23
	sl_wait lmcnt(6)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[72:73], v[74:75], v[0:3]
	.loc	1 20 18                         ; candidate.py:20:18
	ml_slb_load_b32x1  v82, v71, s37, #512, null
	ml_slb_load_b32x1  v83, v71, s37, #768, null
	.loc	1 21 23                         ; candidate.py:21:23
	sl_wait lmcnt(6)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[72:73], v[76:77], v[4:7]
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[72:73], v[78:79], v[8:11]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[72:73], v[80:81], v[12:15]
	.loc	1 20 18                         ; candidate.py:20:18
	ml_slb_load_b32x1  v72, v71, s39, #512, null
	ml_slb_load_b32x1  v73, v71, s39, #768, null
	.loc	1 21 23                         ; candidate.py:21:23
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[82:83], v[74:75], v[16:19]
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[82:83], v[76:77], v[20:23]
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[82:83], v[78:79], v[24:27]
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[82:83], v[80:81], v[28:31]
	.loc	1 20 18                         ; candidate.py:20:18
	ml_slb_load_b32x1  v82, v71, s41, #512, null
	ml_slb_load_b32x1  v83, v71, s41, #768, null
	.loc	1 21 23                         ; candidate.py:21:23
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[72:73], v[74:75], v[32:35]
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[72:73], v[76:77], v[36:39]
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[72:73], v[78:79], v[40:43]
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[72:73], v[80:81], v[44:47]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[48:51], v[82:83], v[74:75], v[48:51]
	ml_matrix_mad_f32_bf16_m16n16k16 v[52:55], v[82:83], v[76:77], v[52:55]
	ml_matrix_mad_f32_bf16_m16n16k16 v[56:59], v[82:83], v[78:79], v[56:59]
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[82:83], v[80:81], v[60:63]
	.loc	1 19 23                         ; candidate.py:19:23
	sl_cbr_wcrz BB0_1, wcr
; %bb.2:
	.loc	1 12 27                         ; candidate.py:12:27
	sl_and_b32 {s1, wcr}, s44, 0x1c0
	.loc	1 12 15 is_stmt 0               ; candidate.py:12:15
	sl_add_i32 s94, s16, s17
	sl_add_i32 s53, s94, 0x8
	sl_add_i32 s51, s94, 0x10
	sl_add_i32 s49, s94, 0x18
	sl_add_i32 s47, s94, 0x20
	sl_add_i32 s45, s94, 0x28
	sl_add_i32 s42, s94, 0x30
	sl_add_i32 s41, s94, 0x38
	sl_add_i32 s40, s94, 0x40
	sl_add_i32 s39, s94, 0x48
	sl_add_i32 s38, s94, 0x50
	sl_add_i32 s37, s94, 0x58
	sl_add_i32 s36, s94, 0x60
	sl_add_i32 s35, s94, 0x68
	sl_add_i32 s23, s94, 0x70
	sl_add_i32 s21, s94, 0x78
	sl_add_i32 s19, s94, 0x80
	sl_add_i32 s18, s94, 0x88
	sl_add_i32 s17, s94, 0x90
	sl_add_i32 s16, s94, 0x98
	sl_add_i32 s15, s94, 0xa0
	sl_add_i32 s14, s94, 0xa8
	sl_add_i32 s13, s94, 0xb0
	sl_add_i32 s12, s94, 0xb8
	sl_add_i32 s11, s94, 0xc0
	sl_add_i32 s10, s94, 0xc8
	sl_add_i32 s7, s94, 0xd0
	sl_add_i32 s6, s94, 0xd8
	sl_add_i32 s5, s94, 0xe0
	sl_add_i32 s4, s94, 0xe8
	sl_add_i32 s3, s94, 0xf0
	sl_add_i32 tcr_hi, s94, 0xf8
	.loc	1 19 23 is_stmt 1               ; candidate.py:19:23
	sl_wait g2scnt(0)
	sl_barrier 
	.loc	1 23 21                         ; candidate.py:23:21
	ml_cvt_bf16_f32  v94, v0
	ml_cvt_bf16_f32  v81, v1
	ml_cvt_bf16_f32  v117, v2
	ml_cvt_bf16_f32  v83, v3
	ml_cvt_bf16_f32  v126, v16
	ml_cvt_bf16_f32  v86, v17
	ml_cvt_bf16_f32  v131, v18
	ml_cvt_bf16_f32  v118, v19
	ml_cvt_bf16_f32  v132, v32
	ml_cvt_bf16_f32  v119, v33
	ml_cvt_bf16_f32  v133, v34
	ml_cvt_bf16_f32  v122, v35
	ml_cvt_bf16_f32  v134, v48
	ml_cvt_bf16_f32  v124, v49
	ml_cvt_bf16_f32  v135, v50
	ml_cvt_bf16_f32  v128, v51
	ml_cvt_bf16_f32  v32, v4
	ml_cvt_bf16_f32  v33, v5
	ml_cvt_bf16_f32  v34, v6
	ml_cvt_bf16_f32  v35, v7
	ml_cvt_bf16_f32  v110, v20
	ml_cvt_bf16_f32  v66, v21
	ml_cvt_bf16_f32  v120, v22
	ml_cvt_bf16_f32  v78, v23
	ml_cvt_bf16_f32  v121, v36
	ml_cvt_bf16_f32  v79, v37
	ml_cvt_bf16_f32  v123, v38
	ml_cvt_bf16_f32  v84, v39
	ml_cvt_bf16_f32  v125, v52
	ml_cvt_bf16_f32  v105, v53
	ml_cvt_bf16_f32  v130, v54
	ml_cvt_bf16_f32  v108, v55
	ml_cvt_bf16_f32  v52, v8
	ml_cvt_bf16_f32  v50, v9
	ml_cvt_bf16_f32  v55, v10
	ml_cvt_bf16_f32  v51, v11
	ml_cvt_bf16_f32  v68, v24
	ml_cvt_bf16_f32  v53, v25
	ml_cvt_bf16_f32  v82, v26
	ml_cvt_bf16_f32  v54, v27
	ml_cvt_bf16_f32  v102, v40
	ml_cvt_bf16_f32  v67, v41
	ml_cvt_bf16_f32  v104, v42
	ml_cvt_bf16_f32  v69, v43
	ml_cvt_bf16_f32  v107, v56
	ml_cvt_bf16_f32  v56, v57
	ml_cvt_bf16_f32  v109, v58
	ml_cvt_bf16_f32  v80, v59
	ml_cvt_bf16_f32  v57, v12
	ml_cvt_bf16_f32  v48, v13
	ml_cvt_bf16_f32  v59, v14
	ml_cvt_bf16_f32  v49, v15
	ml_cvt_bf16_f32  v101, v28
	ml_cvt_bf16_f32  v3, v29
	ml_cvt_bf16_f32  v8, v30
	ml_cvt_bf16_f32  v4, v31
	ml_cvt_bf16_f32  v10, v44
	ml_cvt_bf16_f32  v5, v45
	ml_cvt_bf16_f32  v11, v46
	ml_cvt_bf16_f32  v6, v47
	ml_cvt_bf16_f32  v12, v60
	ml_cvt_bf16_f32  v7, v61
	ml_cvt_bf16_f32  v13, v62
	ml_cvt_bf16_f32  v9, v63
	.loc	1 25 10                         ; candidate.py:25:10
	sl_cmp_lt_u32 wcr, s43, 0x12
	sl_sub_bi_u32 s2, s8, s8, wcr
	.loc	1 25 7 is_stmt 0                ; candidate.py:25:7
	ml_mov_s2v_b32 v242, s3, 0x10
	ml_mov_s2v_b32 v242, s4, 0x11
	ml_mov_s2v_b32 v242, s5, 0x12
	ml_mov_s2v_b32 v242, s6, 0x13
	ml_mov_s2v_b32 v242, s7, 0x14
	ml_mov_s2v_b32 v242, s10, 0x15
	ml_mov_s2v_b32 v242, s11, 0x16
	ml_mov_s2v_b32 v242, s12, 0x17
	ml_mov_s2v_b32 v242, s13, 0x18
	ml_mov_s2v_b32 v242, s14, 0x19
	ml_mov_s2v_b32 v242, s15, 0x1a
	ml_mov_s2v_b32 v242, s16, 0x1b
	ml_mov_s2v_b32 v242, s17, 0x1c
	ml_mov_s2v_b32 v242, s18, 0x1d
	ml_mov_s2v_b32 v242, s19, 0x1e
	ml_mov_s2v_b32 v242, s21, 0x1f
	ml_mov_s2v_b32 v242, s23, 0x20
	ml_mov_s2v_b32 v242, s35, 0x21
	ml_mov_s2v_b32 v242, s36, 0x22
	ml_mov_s2v_b32 v242, s37, 0x23
	ml_mov_s2v_b32 v242, s38, 0x24
	ml_mov_s2v_b32 v242, s39, 0x25
	ml_mov_s2v_b32 v242, s40, 0x26
	ml_mov_s2v_b32 v242, s41, 0x27
	ml_mov_s2v_b32 v242, s42, 0x28
	ml_mov_s2v_b32 v242, s45, 0x29
	ml_mov_s2v_b32 v242, s47, 0x2a
	ml_mov_s2v_b32 v242, s49, 0x2b
	ml_mov_s2v_b32 v242, s51, 0x2c
	ml_mov_s2v_b32 v242, s53, 0x2d
	.loc	1 0 0                           ; candidate.py:0
	ml_and_b32 v0, v70, 0xdf0
	.loc	1 25 7                          ; candidate.py:25:7
	sl_cbr_wcrz BB0_4, wcr
; %bb.3:
	.loc	1 28 37 is_stmt 1               ; candidate.py:28:37
	ml_shl_b32 v1, tid, 0xe
	ml_and_b32 v14, v1, 0x4000
	sl_and_b32 {s0, wcr}, s44, 0x40
	ml_mov_s2v_b32 v242, s0, 0x2e
	sl_mull_u32 s0, s0, 0x200
	sl_mov_b32 tcr_lo, 0x1000504
	ml_byte_permute_b32 v19, v135, v134, tcr_lo
	ml_byte_permute_b32 v18, v133, v132, tcr_lo
	ml_byte_permute_b32 v17, v131, v126, tcr_lo
	ml_byte_permute_b32 v16, v117, v94, tcr_lo
	ml_or_b32 v15, v0, v14
	ml_slb_store_b32x4  v[16:19], v15, s0, #0, null
	ml_mov_s2v_b32 v242, s2, 0x30
	ml_byte_permute_b32 v19, v128, v124, tcr_lo
	ml_byte_permute_b32 v18, v122, v119, tcr_lo
	ml_byte_permute_b32 v17, v118, v86, tcr_lo
	ml_byte_permute_b32 v16, v83, v81, tcr_lo
	ml_slb_store_b32x4  v[16:19], v15, s0, #512, null
	sl_add_i32 s2, s0, 0x1000
	ml_byte_permute_b32 v19, v130, v125, tcr_lo
	ml_byte_permute_b32 v18, v123, v121, tcr_lo
	ml_byte_permute_b32 v17, v120, v110, tcr_lo
	ml_byte_permute_b32 v16, v34, v32, tcr_lo
	ml_slb_store_b32x4  v[16:19], v15, s2, #0, null
	sl_nop 0x0
	ml_byte_permute_b32 v19, v108, v105, tcr_lo
	ml_byte_permute_b32 v18, v84, v79, tcr_lo
	ml_byte_permute_b32 v17, v78, v66, tcr_lo
	ml_byte_permute_b32 v16, v35, v33, tcr_lo
	ml_slb_store_b32x4  v[16:19], v15, s2, #512, null
	sl_add_i32 s2, s0, 0x2000
	ml_byte_permute_b32 v19, v109, v107, tcr_lo
	ml_byte_permute_b32 v18, v104, v102, tcr_lo
	ml_byte_permute_b32 v17, v82, v68, tcr_lo
	ml_byte_permute_b32 v16, v55, v52, tcr_lo
	ml_slb_store_b32x4  v[16:19], v15, s2, #0, null
	sl_add_i32 s0, s0, 0x3000
	ml_byte_permute_b32 v19, v80, v56, tcr_lo
	ml_byte_permute_b32 v18, v69, v67, tcr_lo
	ml_byte_permute_b32 v17, v54, v53, tcr_lo
	ml_byte_permute_b32 v16, v51, v50, tcr_lo
	ml_slb_store_b32x4  v[16:19], v15, s2, #512, null
	sl_nop 0x0
	ml_byte_permute_b32 v19, v13, v12, tcr_lo
	ml_byte_permute_b32 v18, v11, v10, tcr_lo
	ml_byte_permute_b32 v17, v8, v101, tcr_lo
	ml_byte_permute_b32 v16, v59, v57, tcr_lo
	ml_slb_store_b32x4  v[16:19], v15, s0, #0, null
	sl_nop 0x0
	ml_byte_permute_b32 v19, v9, v7, tcr_lo
	ml_byte_permute_b32 v18, v6, v5, tcr_lo
	ml_byte_permute_b32 v17, v4, v3, tcr_lo
	ml_byte_permute_b32 v16, v49, v48, tcr_lo
	ml_slb_store_b32x4  v[16:19], v15, s0, #512, null
	.loc	1 15 12                         ; candidate.py:15:12
	sl_mulh_i32 s0, tcr_hi, 0x81228dbf
	sl_add_i32 s0, s0, tcr_hi
	sl_srl_b32 {s2, wcr}, s0, 0x1f
	sl_sra_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s2
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s0, tcr_hi, s0
	ml_mov_s2v_b32 v242, s0, 0x32
	ml_mov_s2v_b32 v242, s1, 0x33
	sl_mulh_i32 s0, s3, 0x81228dbf
	sl_add_i32 s0, s0, s3
	sl_srl_b32 {s2, wcr}, s0, 0x1f
	sl_sra_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s2
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s0, s3, s0
	ml_mov_s2v_b32 v242, s0, 0x36
	ml_mov_s2v_b32 v242, s1, 0x37
	sl_mulh_i32 s0, s4, 0x81228dbf
	sl_add_i32 s0, s0, s4
	sl_srl_b32 {s2, wcr}, s0, 0x1f
	sl_sra_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s2
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s0, s4, s0
	ml_mov_s2v_b32 v242, s0, 0x3a
	ml_mov_s2v_b32 v242, s1, 0x3b
	sl_mulh_i32 s0, s5, 0x81228dbf
	sl_add_i32 s0, s0, s5
	sl_srl_b32 {s2, wcr}, s0, 0x1f
	sl_sra_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s2
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s0, s5, s0
	ml_mov_s2v_b32 v242, s0, 0x3e
	ml_mov_s2v_b32 v242, s1, 0x3f
	sl_mulh_i32 s0, s6, 0x81228dbf
	sl_add_i32 s0, s0, s6
	sl_srl_b32 {s2, wcr}, s0, 0x1f
	sl_sra_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s2
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s32, s6, s0
	sl_mulh_i32 s0, s7, 0x81228dbf
	sl_add_i32 s0, s0, s7
	sl_srl_b32 {s2, wcr}, s0, 0x1f
	sl_sra_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s2
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s0, s7, s0
	ml_mov_s2v_b32 v243, s0, 0x2
	ml_mov_s2v_b32 v243, s1, 0x3
	sl_mulh_i32 s0, s10, 0x81228dbf
	sl_add_i32 s0, s0, s10
	sl_srl_b32 {s2, wcr}, s0, 0x1f
	sl_sra_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s2
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s10, s10, s0
	sl_mulh_i32 s0, s11, 0x81228dbf
	sl_add_i32 s0, s0, s11
	sl_srl_b32 {s2, wcr}, s0, 0x1f
	sl_sra_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s2
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s0, s11, s0
	ml_mov_s2v_b32 v243, s0, 0x6
	ml_mov_s2v_b32 v243, s1, 0x7
	sl_mulh_i32 s0, s12, 0x81228dbf
	sl_add_i32 s0, s0, s12
	sl_srl_b32 {s2, wcr}, s0, 0x1f
	sl_sra_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s2
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s0, s12, s0
	ml_mov_s2v_b32 v243, s0, 0xa
	ml_mov_s2v_b32 v243, s1, 0xb
	sl_mulh_i32 s0, s13, 0x81228dbf
	sl_add_i32 s0, s0, s13
	sl_srl_b32 {s2, wcr}, s0, 0x1f
	sl_sra_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s2
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s0, s13, s0
	ml_mov_s2v_b32 v243, s0, 0xe
	ml_mov_s2v_b32 v243, s1, 0xf
	sl_mulh_i32 s0, s14, 0x81228dbf
	sl_add_i32 s0, s0, s14
	sl_srl_b32 {s2, wcr}, s0, 0x1f
	sl_sra_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s2
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s92, s14, s0
	sl_mulh_i32 s0, s15, 0x81228dbf
	sl_add_i32 s0, s0, s15
	sl_srl_b32 {s2, wcr}, s0, 0x1f
	sl_sra_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s2
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s34, s15, s0
	sl_mulh_i32 s0, s16, 0x81228dbf
	sl_add_i32 s0, s0, s16
	sl_srl_b32 {s2, wcr}, s0, 0x1f
	sl_sra_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s2
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s2, s16, s0
	sl_mulh_i32 s0, s17, 0x81228dbf
	sl_add_i32 s0, s0, s17
	sl_srl_b32 {s3, wcr}, s0, 0x1f
	sl_sra_b32 {s0, wcr}, s0, 0xa
	sl_add_i32 s0, s0, s3
	sl_mull_u32 s0, s0, 0x7ee
	sl_sub_i32 s0, s17, s0
	sl_mulh_i32 s3, s18, 0x81228dbf
	sl_add_i32 s3, s3, s18
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s20, s18, s3
	sl_mulh_i32 s3, s19, 0x81228dbf
	sl_add_i32 s3, s3, s19
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s22, s19, s3
	sl_mulh_i32 s3, s21, 0x81228dbf
	sl_add_i32 s3, s3, s21
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	ml_mov_s2v_b32 v243, s44, 0x12
	sl_sub_i32 s44, s21, s3
	sl_mulh_i32 s3, s23, 0x81228dbf
	sl_add_i32 s3, s3, s23
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s46, s23, s3
	sl_mulh_i32 s3, s35, 0x81228dbf
	sl_add_i32 s3, s3, s35
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s16, s35, s3
	sl_mulh_i32 s3, s36, 0x81228dbf
	sl_add_i32 s3, s3, s36
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s12, s36, s3
	sl_mulh_i32 s3, s37, 0x81228dbf
	sl_add_i32 s3, s3, s37
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s14, s37, s3
	sl_mulh_i32 s3, s38, 0x81228dbf
	sl_add_i32 s3, s3, s38
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s18, s38, s3
	sl_mulh_i32 s3, s39, 0x81228dbf
	sl_add_i32 s3, s3, s39
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s48, s39, s3
	sl_mulh_i32 s3, s40, 0x81228dbf
	sl_add_i32 s3, s3, s40
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s50, s40, s3
	sl_mulh_i32 s3, s41, 0x81228dbf
	sl_add_i32 s3, s3, s41
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s56, s41, s3
	sl_mulh_i32 s3, s42, 0x81228dbf
	sl_add_i32 s3, s3, s42
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s52, s42, s3
	sl_mulh_i32 s3, s45, 0x81228dbf
	sl_add_i32 s3, s3, s45
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s54, s45, s3
	sl_mulh_i32 s3, s47, 0x81228dbf
	sl_add_i32 s3, s3, s47
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s58, s47, s3
	sl_mulh_i32 s3, s49, 0x81228dbf
	sl_add_i32 s3, s3, s49
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s60, s49, s3
	sl_mulh_i32 s3, s51, 0x81228dbf
	sl_add_i32 s3, s3, s51
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s40, s51, s3
	sl_mulh_i32 s3, s53, 0x81228dbf
	sl_add_i32 s3, s3, s53
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s36, s53, s3
	sl_mulh_i32 s3, s94, 0x81228dbf
	sl_add_i32 s3, s3, s94
	sl_srl_b32 {s4, wcr}, s3, 0x1f
	sl_sra_b32 {s3, wcr}, s3, 0xa
	sl_add_i32 s3, s3, s4
	sl_mull_u32 s3, s3, 0x7ee
	sl_sub_i32 s4, s94, s3
	.loc	1 28 37                         ; candidate.py:28:37
	sl_mov_b32 s11, 0x0
	sl_wait lmcnt(0)
	sl_barrier 
	ml_shl_b32 v1, v64, 0x8
	ml_and_b32 v1, v1, 0x3000
	ml_and_b32 v2, v65, 0x70
	sl_mull_u32 s1, s1, 0x2
	ml_mov_s2v_b32 v243, s1, 0x14
	ml_and_b32 v129, tid, 0x8
	ml_shl_b32 v16, v129, 0xc
	ml_anyop3_b32 v127, v1, v2, s1, 0xfffffffe
	ml_or_b32 v58, v127, v16
	ml_slb_load_b32x4  v[16:19], v58, noreg, #0, null
	sl_mov_b32 s1, 0x4000
	ml_xor_b32 v136, tid, 0x20
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v32, v32, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_load_b32x4  v[20:23], v58, s1, #0, null
	sl_mov_b32 s1, 0x400
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v33, v33, 0x10
	ml_shl_b32 v34, v34, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_load_b32x4  v[24:27], v58, s1, #0, null
	sl_mov_b32 s1, 0x4400
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v35, v35, 0x10
	ml_shl_b32 v50, v50, 0x10
	ml_shl_b32 v57, v57, 0x10
	ml_shl_b32 v48, v48, 0x10
	ml_shl_b32 v59, v59, 0x10
	ml_shl_b32 v49, v49, 0x10
	.loc	1 30 28                         ; candidate.py:30:28
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x3
	ml_mov_v2s_b32 s64, v242, 0x0
	ml_mov_v2s_b32 s65, v242, 0x1
	.loc	1 28 37                         ; candidate.py:28:37
	sl_wait lmcnt(2)
	ml_shl_b32 v28, v16, 0x10
	ml_sra_b32 v28, v28, 0x10
	ml_slb_shuffle_rtn_b32 v70, v28, v136
	ml_sra_b32 v16, v16, 0x10
	sl_wait lmcnt(2)
	ml_shl_b32 v36, v20, 0x10
	ml_sra_b32 v65, v36, 0x10
	ml_slb_load_b32x4  v[28:31], v58, s1, #0, null
	sl_mov_b32 s1, 0x800
	ml_sra_b32 v20, v20, 0x10
	sl_wait lmcnt(2)
	ml_shl_b32 v44, v24, 0x10
	ml_slb_load_b32x4  v[36:39], v58, s1, #0, null
	sl_mov_b32 s1, 0x4800
	ml_sra_b32 v71, v44, 0x10
	ml_sra_b32 v24, v24, 0x10
	ml_slb_load_b32x4  v[40:43], v58, s1, #0, null
	sl_mov_b32 s1, 0xc00
	ml_shl_b32 v73, v17, 0x10
	ml_sra_b32 v85, v73, 0x10
	ml_slb_load_b32x4  v[44:47], v58, s1, #0, null
	sl_mov_b32 s1, 0x4c00
	ml_sra_b32 v17, v17, 0x10
	ml_sra_b32 v137, v22, 0x10
	ml_slb_shuffle_rtn_b32 v92, v65, v136
	ml_sra_b32 v139, v26, 0x10
	ml_sra_b32 v151, v19, 0x10
	ml_sra_b32 v152, v23, 0x10
	sl_wait lmcnt(4)
	ml_shl_b32 v60, v28, 0x10
	ml_sra_b32 v72, v60, 0x10
	ml_slb_load_b32x4  v[60:63], v58, s1, #0, null
	ml_sra_b32 v28, v28, 0x10
	sl_wait lmcnt(4)
	ml_shl_b32 v58, v36, 0x10
	ml_sra_b32 v58, v58, 0x10
	ml_slb_shuffle_rtn_b32 v75, v16, v136
	ml_sra_b32 v16, v36, 0x10
	sl_wait lmcnt(4)
	ml_shl_b32 v65, v40, 0x10
	ml_sra_b32 v65, v65, 0x10
	ml_sra_b32 v36, v40, 0x10
	ml_slb_shuffle_rtn_b32 v95, v20, v136
	sl_wait lmcnt(4)
	ml_shl_b32 v40, v44, 0x10
	ml_sra_b32 v20, v40, 0x10
	ml_sra_b32 v44, v44, 0x10
	ml_slb_shuffle_rtn_b32 v71, v71, v136
	ml_sra_b32 v140, v30, 0x10
	ml_sra_b32 v143, v38, 0x10
	ml_sra_b32 v144, v42, 0x10
	ml_slb_shuffle_rtn_b32 v96, v72, v136
	ml_shl_b32 v72, v21, 0x10
	ml_sra_b32 v87, v72, 0x10
	sl_wait lmcnt(4)
	ml_shl_b32 v40, v60, 0x10
	ml_sra_b32 v40, v40, 0x10
	ml_sra_b32 v60, v60, 0x10
	ml_slb_shuffle_rtn_b32 v74, v24, v136
	ml_sra_b32 v21, v21, 0x10
	ml_shl_b32 v24, v25, 0x10
	ml_sra_b32 v24, v24, 0x10
	ml_slb_shuffle_rtn_b32 v97, v28, v136
	ml_shl_b32 v28, v29, 0x10
	ml_sra_b32 v28, v28, 0x10
	ml_sra_b32 v25, v25, 0x10
	ml_slb_shuffle_rtn_b32 v72, v58, v136
	ml_sra_b32 v29, v29, 0x10
	ml_shl_b32 v58, v37, 0x10
	ml_sra_b32 v58, v58, 0x10
	ml_slb_shuffle_rtn_b32 v98, v65, v136
	ml_shl_b32 v65, v41, 0x10
	ml_sra_b32 v65, v65, 0x10
	ml_sra_b32 v147, v46, 0x10
	ml_slb_shuffle_rtn_b32 v76, v16, v136
	ml_sra_b32 v16, v37, 0x10
	ml_sra_b32 v37, v41, 0x10
	ml_shl_b32 v41, v45, 0x10
	ml_slb_shuffle_rtn_b32 v99, v36, v136
	ml_sra_b32 v36, v41, 0x10
	ml_shl_b32 v41, v61, 0x10
	ml_sra_b32 v41, v41, 0x10
	ml_slb_shuffle_rtn_b32 v73, v20, v136
	ml_sra_b32 v20, v45, 0x10
	ml_sra_b32 v45, v61, 0x10
	ml_shl_b32 v61, v18, 0x10
	ml_slb_shuffle_rtn_b32 v100, v40, v136
	ml_sra_b32 v40, v61, 0x10
	ml_shl_b32 v61, v22, 0x10
	ml_sra_b32 v61, v61, 0x10
	ml_slb_shuffle_rtn_b32 v77, v44, v136
	ml_sra_b32 v44, v18, 0x10
	ml_shl_b32 v18, v26, 0x10
	ml_sra_b32 v148, v62, 0x10
	ml_slb_shuffle_rtn_b32 v103, v60, v136
	ml_sra_b32 v60, v18, 0x10
	ml_shl_b32 v18, v30, 0x10
	ml_sra_b32 v138, v18, 0x10
	ml_slb_shuffle_rtn_b32 v85, v85, v136
	ml_shl_b32 v18, v38, 0x10
	ml_sra_b32 v141, v18, 0x10
	ml_shl_b32 v18, v42, 0x10
	ml_slb_shuffle_rtn_b32 v106, v87, v136
	ml_sra_b32 v142, v18, 0x10
	ml_sra_b32 v155, v27, 0x10
	ml_sra_b32 v156, v31, 0x10
	ml_slb_shuffle_rtn_b32 v90, v17, v136
	ml_shl_b32 v17, v46, 0x10
	ml_sra_b32 v145, v17, 0x10
	ml_shl_b32 v17, v62, 0x10
	ml_slb_shuffle_rtn_b32 v111, v21, v136
	ml_sra_b32 v146, v17, 0x10
	ml_shl_b32 v17, v19, 0x10
	ml_sra_b32 v149, v17, 0x10
	ml_slb_shuffle_rtn_b32 v87, v24, v136
	ml_shl_b32 v17, v23, 0x10
	ml_sra_b32 v150, v17, 0x10
	ml_shl_b32 v17, v27, 0x10
	ml_slb_shuffle_rtn_b32 v112, v28, v136
	ml_sra_b32 v153, v17, 0x10
	ml_shl_b32 v17, v31, 0x10
	ml_sra_b32 v154, v17, 0x10
	ml_slb_shuffle_rtn_b32 v91, v25, v136
	ml_shl_b32 v17, v39, 0x10
	ml_sra_b32 v157, v17, 0x10
	ml_shl_b32 v17, v43, 0x10
	ml_slb_shuffle_rtn_b32 v113, v29, v136
	ml_sra_b32 v158, v17, 0x10
	ml_sra_b32 v159, v39, 0x10
	ml_sra_b32 v160, v43, 0x10
	ml_slb_shuffle_rtn_b32 v88, v58, v136
	ml_sra_b32 v163, v47, 0x10
	ml_sra_b32 v164, v63, 0x10
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v17, v81, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v114, v65, v136
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v18, v117, 0x10
	ml_shl_b32 v19, v83, 0x10
	ml_shl_b32 v21, v86, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v93, v16, v136
	ml_shl_b32 v16, v47, 0x10
	ml_sra_b32 v161, v16, 0x10
	ml_shl_b32 v16, v63, 0x10
	ml_slb_shuffle_rtn_b32 v115, v37, v136
	ml_sra_b32 v162, v16, 0x10
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v16, v94, 0x10
	ml_shl_b32 v22, v131, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v89, v36, v136
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v23, v118, 0x10
	ml_shl_b32 v24, v132, 0x10
	ml_shl_b32 v25, v119, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v116, v41, v136
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v26, v133, 0x10
	ml_shl_b32 v27, v122, 0x10
	ml_shl_b32 v28, v134, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v94, v20, v136
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v20, v126, 0x10
	ml_shl_b32 v29, v124, 0x10
	ml_shl_b32 v30, v135, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v117, v45, v136
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v31, v128, 0x10
	ml_shl_b32 v36, v110, 0x10
	ml_shl_b32 v37, v66, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v83, v40, v136
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v38, v120, 0x10
	ml_shl_b32 v39, v78, 0x10
	ml_shl_b32 v40, v121, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v118, v61, v136
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v41, v79, 0x10
	ml_shl_b32 v42, v123, 0x10
	ml_shl_b32 v43, v84, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v86, v44, v136
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v44, v125, 0x10
	ml_shl_b32 v45, v105, 0x10
	ml_shl_b32 v46, v130, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v119, v137, v136
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v47, v108, 0x10
	ml_shl_b32 v63, v52, 0x10
	ml_shl_b32 v65, v55, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v81, v60, v136
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v52, v51, 0x10
	ml_shl_b32 v66, v68, 0x10
	ml_shl_b32 v55, v53, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v120, v138, v136
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v68, v82, 0x10
	ml_shl_b32 v58, v54, 0x10
	ml_shl_b32 v60, v102, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v84, v139, v136
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v51, v67, 0x10
	ml_shl_b32 v61, v104, 0x10
	ml_shl_b32 v53, v69, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v121, v140, v136
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v67, v107, 0x10
	ml_shl_b32 v54, v56, 0x10
	ml_shl_b32 v69, v109, 0x10
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v79, v141, v136
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v56, v80, 0x10
	ml_shl_b32 v62, v101, 0x10
	ml_mov_v2s_b32 s66, v242, 0x2
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v122, v142, v136
	ml_mov_v2s_b32 s67, v242, 0x3
	ml_mov_v2s_b32 s68, v242, 0x4
	ml_mov_v2s_b32 s69, v242, 0x5
	ml_slb_shuffle_rtn_b32 v82, v143, v136
	ml_mov_v2s_b32 s70, v242, 0x6
	ml_mov_v2s_b32 s71, v242, 0x7
	ml_mov_v2s_b32 s72, v242, 0x8
	ml_slb_shuffle_rtn_b32 v123, v144, v136
	ml_mov_v2s_b32 s73, v242, 0x9
	ml_mov_v2s_b32 s74, v242, 0xa
	ml_mov_v2s_b32 s75, v242, 0xb
	ml_slb_shuffle_rtn_b32 v78, v145, v136
	ml_mov_v2s_b32 s76, v242, 0xc
	ml_mov_v2s_b32 s77, v242, 0xd
	ml_mov_v2s_b32 s78, v242, 0xe
	ml_slb_shuffle_rtn_b32 v124, v146, v136
	ml_mov_v2s_b32 s79, v242, 0xf
	.loc	1 30 28                         ; candidate.py:30:28
	sl_mov_b32 s83, 0xffffffff
	sl_sra_b32 {s37, wcr}, s36, 0x1f
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v80, v147, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_add_i64 s[80:81], s[68:69], s[4:5]
	sl_shl_b64 {s[36:37], wcr}, s[36:37], 0x3
	sl_add_i64 s[36:37], s[68:69], s[36:37]
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v125, v148, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_mov_b64 s[38:39], s[82:83]
	sl_sra_b32 {s41, wcr}, s40, 0x1f
	sl_shl_b64 {s[40:41], wcr}, s[40:41], 0x3
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v101, v149, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_add_i64 s[40:41], s[68:69], s[40:41]
	ml_mov_s2v_b32 v243, s43, 0x16
	sl_mov_b64 s[42:43], s[82:83]
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v126, v150, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_sra_b32 {s61, wcr}, s60, 0x1f
	sl_shl_b64 {s[60:61], wcr}, s[60:61], 0x3
	sl_add_i64 s[28:29], s[68:69], s[60:61]
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v107, v151, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_mov_b64 s[30:31], s[82:83]
	sl_sra_b32 {s59, wcr}, s58, 0x1f
	sl_shl_b64 {s[58:59], wcr}, s[58:59], 0x3
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v128, v152, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_add_i64 s[84:85], s[68:69], s[58:59]
	sl_mov_b64 s[86:87], s[82:83]
	sl_sra_b32 {s55, wcr}, s54, 0x1f
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v102, v153, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_shl_b64 {s[54:55], wcr}, s[54:55], 0x3
	sl_add_i64 s[88:89], s[68:69], s[54:55]
	sl_mov_b64 s[90:91], s[82:83]
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v130, v154, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_sra_b32 {s53, wcr}, s52, 0x1f
	sl_shl_b64 {s[52:53], wcr}, s[52:53], 0x3
	sl_add_i64 s[52:53], s[68:69], s[52:53]
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v108, v155, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_mov_b64 s[54:55], s[82:83]
	sl_sra_b32 {s57, wcr}, s56, 0x1f
	sl_shl_b64 {s[56:57], wcr}, s[56:57], 0x3
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v131, v156, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_add_i64 s[56:57], s[68:69], s[56:57]
	sl_mov_b64 s[58:59], s[82:83]
	sl_sra_b32 {s51, wcr}, s50, 0x1f
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v104, v157, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_shl_b64 {s[50:51], wcr}, s[50:51], 0x3
	sl_add_i64 s[60:61], s[68:69], s[50:51]
	sl_mov_b64 s[62:63], s[82:83]
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v132, v158, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_sra_b32 {s49, wcr}, s48, 0x1f
	sl_shl_b64 {s[48:49], wcr}, s[48:49], 0x3
	sl_add_i64 s[72:73], s[68:69], s[48:49]
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v109, v159, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_mov_b64 s[74:75], s[82:83]
	sl_sra_b32 {s19, wcr}, s18, 0x1f
	sl_shl_b64 {s[18:19], wcr}, s[18:19], 0x3
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v133, v160, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_add_i64 s[76:77], s[68:69], s[18:19]
	sl_mov_b64 s[78:79], s[82:83]
	sl_sra_b32 {s15, wcr}, s14, 0x1f
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v105, v161, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_shl_b64 {s[14:15], wcr}, s[14:15], 0x3
	sl_add_i64 s[24:25], s[68:69], s[14:15]
	sl_mov_b64 s[26:27], s[82:83]
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v134, v162, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_sra_b32 {s13, wcr}, s12, 0x1f
	sl_shl_b64 {s[12:13], wcr}, s[12:13], 0x3
	sl_add_i64 s[12:13], s[68:69], s[12:13]
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v110, v163, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_mov_b64 s[14:15], s[82:83]
	sl_sra_b32 {s17, wcr}, s16, 0x1f
	sl_shl_b64 {s[16:17], wcr}, s[16:17], 0x3
	.loc	1 28 37                         ; candidate.py:28:37
	ml_slb_shuffle_rtn_b32 v135, v164, v136
	.loc	1 30 28                         ; candidate.py:30:28
	sl_add_i64 s[16:17], s[68:69], s[16:17]
	sl_mov_b64 s[18:19], s[82:83]
	sl_sra_b32 {s47, wcr}, s46, 0x1f
	sl_shl_b64 {s[46:47], wcr}, s[46:47], 0x3
	sl_add_i64 s[64:65], s[68:69], s[46:47]
	sl_mov_b64 s[66:67], s[82:83]
	sl_sra_b32 {s45, wcr}, s44, 0x1f
	sl_shl_b64 {s[44:45], wcr}, s[44:45], 0x3
	sl_add_i64 s[48:49], s[68:69], s[44:45]
	sl_mov_b64 s[50:51], s[82:83]
	sl_sra_b32 {s23, wcr}, s22, 0x1f
	sl_shl_b64 {s[22:23], wcr}, s[22:23], 0x3
	sl_add_i64 s[44:45], s[68:69], s[22:23]
	sl_mov_b64 s[46:47], s[82:83]
	sl_sra_b32 {s21, wcr}, s20, 0x1f
	sl_shl_b64 {s[20:21], wcr}, s[20:21], 0x3
	sl_add_i64 s[20:21], s[68:69], s[20:21]
	sl_mov_b64 s[22:23], s[82:83]
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x3
	sl_add_i64 s[4:5], s[68:69], s[0:1]
	sl_mov_b64 s[6:7], s[82:83]
	ml_mov_s2v_b32 v243, s4, 0x18
	ml_mov_s2v_b32 v243, s5, 0x19
	ml_mov_s2v_b32 v243, s6, 0x1a
	ml_mov_s2v_b32 v243, s7, 0x1b
	sl_sra_b32 {s3, wcr}, s2, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[2:3], 0x3
	sl_add_i64 s[0:1], s[68:69], s[0:1]
	sl_mov_b64 s[2:3], s[82:83]
	ml_mov_s2v_b32 v243, s0, 0x1c
	ml_mov_s2v_b32 v243, s1, 0x1d
	ml_mov_s2v_b32 v243, s2, 0x1e
	ml_mov_s2v_b32 v243, s3, 0x1f
	sl_sra_b32 {s35, wcr}, s34, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[34:35], 0x3
	sl_add_i64 s[0:1], s[68:69], s[0:1]
	ml_mov_s2v_b32 v243, s0, 0x20
	ml_mov_s2v_b32 v243, s1, 0x21
	ml_mov_s2v_b32 v243, s2, 0x22
	ml_mov_s2v_b32 v243, s3, 0x23
	sl_sra_b32 {s93, wcr}, s92, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[92:93], 0x3
	.loc	1 30 18 is_stmt 0               ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[136:137], s[80:83], noreg, noreg, #0, ca
	.loc	1 30 28                         ; candidate.py:30:28
	sl_add_i64 s[0:1], s[68:69], s[0:1]
	ml_mov_v2s_b32 s4, v243, 0xe
	ml_mov_v2s_b32 s5, v243, 0xf
	.loc	1 30 18                         ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[138:139], s[36:39], noreg, noreg, #0, ca
	.loc	1 29 27 is_stmt 1               ; candidate.py:29:27
	ml_shl_b32 v10, v10, 0x10
	.loc	1 30 28                         ; candidate.py:30:28
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x3
	sl_add_i64 s[36:37], s[68:69], s[4:5]
	.loc	1 30 18 is_stmt 0               ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[140:141], s[40:43], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s4, v243, 0xa
	ml_mov_v2s_b32 s5, v243, 0xb
	.loc	1 29 27 is_stmt 1               ; candidate.py:29:27
	ml_shl_b32 v11, v11, 0x10
	.loc	1 30 18                         ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[142:143], s[28:31], noreg, noreg, #0, ca
	.loc	1 30 28 is_stmt 0               ; candidate.py:30:28
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x3
	sl_add_i64 s[40:41], s[68:69], s[4:5]
	ml_mov_v2s_b32 s4, v243, 0x6
	ml_mov_v2s_b32 s5, v243, 0x7
	.loc	1 30 18                         ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[144:145], s[84:87], noreg, noreg, #0, ca
	.loc	1 30 28                         ; candidate.py:30:28
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x3
	sl_add_i64 s[28:29], s[68:69], s[4:5]
	sl_mov_b32 s4, s10
	sl_sra_b32 {s5, wcr}, s10, 0x1f
	.loc	1 30 18                         ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[146:147], s[88:91], noreg, noreg, #0, ca
	.loc	1 30 28                         ; candidate.py:30:28
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x3
	sl_add_i64 s[84:85], s[68:69], s[4:5]
	ml_mov_v2s_b32 s4, v243, 0x2
	.loc	1 30 18                         ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[148:149], s[52:55], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s5, v243, 0x3
	.loc	1 30 28                         ; candidate.py:30:28
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x3
	sl_add_i64 s[52:53], s[68:69], s[4:5]
	.loc	1 30 18                         ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[150:151], s[56:59], noreg, noreg, #0, ca
	sl_mov_b32 s4, s32
	.loc	1 30 28                         ; candidate.py:30:28
	sl_sra_b32 {s5, wcr}, s32, 0x1f
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x3
	.loc	1 30 18                         ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[152:153], s[60:63], noreg, noreg, #0, ca
	.loc	1 30 28                         ; candidate.py:30:28
	sl_add_i64 s[56:57], s[68:69], s[4:5]
	ml_mov_v2s_b32 s4, v242, 0x3e
	ml_mov_v2s_b32 s5, v242, 0x3f
	.loc	1 30 18                         ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[154:155], s[72:75], noreg, noreg, #0, ca
	sl_wait vmcnt(5)
	ml_mov_v2s_b32 s34, v144, 0x0
	.loc	1 30 28                         ; candidate.py:30:28
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x3
	sl_add_i64 s[60:61], s[68:69], s[4:5]
	.loc	1 30 18                         ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[156:157], s[76:79], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s4, v242, 0x3a
	ml_mov_v2s_b32 s5, v242, 0x3b
	ml_mov_v2s_b32 s35, v145, 0x0
	ml_lsa_load_dwordx2 v[158:159], s[24:27], noreg, noreg, #0, ca
	.loc	1 30 28                         ; candidate.py:30:28
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x3
	sl_add_i64 s[72:73], s[68:69], s[4:5]
	ml_mov_v2s_b32 s4, v242, 0x36
	ml_mov_v2s_b32 s5, v242, 0x37
	.loc	1 30 18                         ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[160:161], s[12:15], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s26, v136, 0x0
	.loc	1 30 28                         ; candidate.py:30:28
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x3
	sl_add_i64 s[12:13], s[68:69], s[4:5]
	ml_mov_v2s_b32 s4, v242, 0x32
	ml_mov_v2s_b32 s5, v242, 0x33
	.loc	1 30 18                         ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[162:163], s[16:19], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s27, v137, 0x0
	.loc	1 30 28                         ; candidate.py:30:28
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x3
	sl_add_i64 s[16:17], s[68:69], s[4:5]
	.loc	1 30 18                         ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[164:165], s[64:67], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s24, v138, 0x0
	ml_mov_v2s_b32 s25, v139, 0x0
	ml_mov_v2s_b32 s4, v243, 0x18
	ml_lsa_load_dwordx2 v[136:137], s[48:51], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s48, v140, 0x0
	ml_mov_v2s_b32 s49, v141, 0x0
	ml_mov_v2s_b32 s5, v243, 0x19
	ml_lsa_load_dwordx2 v[138:139], s[44:47], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s46, v142, 0x0
	ml_mov_v2s_b32 s47, v143, 0x0
	ml_mov_v2s_b32 s6, v243, 0x1a
	ml_lsa_load_dwordx2 v[140:141], s[20:23], noreg, noreg, #0, ca
	sl_wait vmcnt(12)
	ml_mov_v2s_b32 s22, v146, 0x0
	ml_mov_v2s_b32 s23, v147, 0x0
	ml_mov_v2s_b32 s7, v243, 0x1b
	sl_wait vmcnt(11)
	ml_mov_v2s_b32 s64, v148, 0x0
	ml_mov_v2s_b32 s65, v149, 0x0
	sl_wait vmcnt(10)
	ml_mov_v2s_b32 s20, v150, 0x0
	ml_lsa_load_dwordx2 v[142:143], s[4:7], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s4, v243, 0x1c
	ml_mov_v2s_b32 s5, v243, 0x1d
	ml_mov_v2s_b32 s6, v243, 0x1e
	ml_mov_v2s_b32 s7, v243, 0x1f
	ml_mov_v2s_b32 s21, v151, 0x0
	sl_wait vmcnt(10)
	ml_mov_v2s_b32 s50, v152, 0x0
	ml_mov_v2s_b32 s51, v153, 0x0
	ml_lsa_load_dwordx2 v[144:145], s[4:7], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s4, v243, 0x20
	ml_mov_v2s_b32 s5, v243, 0x21
	ml_mov_v2s_b32 s6, v243, 0x22
	ml_mov_v2s_b32 s7, v243, 0x23
	sl_wait vmcnt(10)
	ml_mov_v2s_b32 s76, v154, 0x0
	ml_mov_v2s_b32 s77, v155, 0x0
	sl_wait vmcnt(9)
	ml_mov_v2s_b32 s44, v156, 0x0
	ml_lsa_load_dwordx2 v[146:147], s[4:7], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s45, v157, 0x0
	sl_wait vmcnt(9)
	ml_mov_v2s_b32 s66, v158, 0x0
	ml_mov_v2s_b32 s67, v159, 0x0
	ml_lsa_load_dwordx2 v[148:149], s[0:3], noreg, noreg, #0, ca
	sl_wait vmcnt(8)
	ml_mov_v2s_b32 s32, v162, 0x0
	ml_mov_v2s_b32 s33, v163, 0x0
	sl_wait vmcnt(6)
	ml_mov_v2s_b32 s88, v136, 0x0
	ml_lsa_load_dwordx2 v[150:151], s[36:39], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s38, v160, 0x0
	ml_mov_v2s_b32 s39, v161, 0x0
	ml_mov_v2s_b32 s89, v137, 0x0
	ml_lsa_load_dwordx2 v[152:153], s[40:43], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s42, v164, 0x0
	ml_mov_v2s_b32 s43, v165, 0x0
	sl_wait vmcnt(7)
	ml_mov_v2s_b32 s68, v138, 0x0
	ml_lsa_load_dwordx2 v[154:155], s[28:31], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s69, v139, 0x0
	sl_wait vmcnt(7)
	ml_mov_v2s_b32 s80, v140, 0x0
	ml_mov_v2s_b32 s81, v141, 0x0
	ml_lsa_load_dwordx2 v[136:137], s[84:87], noreg, noreg, #0, ca
	sl_wait vmcnt(7)
	ml_mov_v2s_b32 s86, v142, 0x0
	ml_mov_v2s_b32 s87, v143, 0x0
	.loc	1 31 36 is_stmt 1               ; candidate.py:31:36
	sl_srl_b32 {s0, wcr}, s27, 0xe
	.loc	1 30 18                         ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[138:139], s[52:55], noreg, noreg, #0, ca
	sl_wait vmcnt(7)
	ml_mov_v2s_b32 s52, v144, 0x0
	ml_mov_v2s_b32 s53, v145, 0x0
	sl_wait vmcnt(6)
	ml_mov_v2s_b32 s54, v146, 0x0
	ml_lsa_load_dwordx2 v[140:141], s[56:59], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s55, v147, 0x0
	sl_wait vmcnt(6)
	ml_mov_v2s_b32 s56, v148, 0x0
	ml_mov_v2s_b32 s57, v149, 0x0
	ml_lsa_load_dwordx2 v[142:143], s[60:63], noreg, noreg, #0, ca
	sl_wait vmcnt(6)
	ml_mov_v2s_b32 s58, v150, 0x0
	ml_mov_v2s_b32 s59, v151, 0x0
	sl_wait vmcnt(5)
	ml_mov_v2s_b32 s90, v152, 0x0
	ml_lsa_load_dwordx2 v[144:145], s[72:75], noreg, noreg, #0, ca
	ml_mov_v2s_b32 s91, v153, 0x0
	sl_wait vmcnt(5)
	ml_mov_v2s_b32 s6, v154, 0x0
	ml_mov_v2s_b32 s7, v155, 0x0
	ml_lsa_load_dwordx2 v[146:147], s[12:15], noreg, noreg, #0, ca
	sl_wait vmcnt(5)
	ml_mov_v2s_b32 s84, v136, 0x0
	ml_mov_v2s_b32 s85, v137, 0x0
	.loc	1 31 36                         ; candidate.py:31:36
	sl_and_b32 {s10, wcr}, s0, 0x20000
	.loc	1 30 18                         ; candidate.py:30:18
	ml_lsa_load_dwordx2 v[148:149], s[16:19], noreg, noreg, #0, ca
	sl_wait vmcnt(5)
	ml_mov_v2s_b32 s92, v138, 0x0
	ml_mov_v2s_b32 s93, v139, 0x0
	.loc	1 31 36                         ; candidate.py:31:36
	sl_add_i64 s[28:29], s[10:11], s[26:27]
	.loc	1 30 18                         ; candidate.py:30:18
	sl_wait vmcnt(4)
	ml_mov_v2s_b32 s82, v140, 0x0
	ml_mov_v2s_b32 s83, v141, 0x0
	.loc	1 31 36                         ; candidate.py:31:36
	sl_srl_b32 {s0, wcr}, s25, 0xe
	sl_and_b32 {s10, wcr}, s0, 0x20000
	.loc	1 30 18                         ; candidate.py:30:18
	sl_wait vmcnt(3)
	ml_mov_v2s_b32 s30, v142, 0x0
	ml_mov_v2s_b32 s31, v143, 0x0
	.loc	1 31 36                         ; candidate.py:31:36
	sl_add_i64 s[0:1], s[10:11], s[24:25]
	sl_srl_b32 {s2, wcr}, s49, 0xe
	.loc	1 30 18                         ; candidate.py:30:18
	sl_wait vmcnt(2)
	ml_mov_v2s_b32 s62, v144, 0x0
	ml_mov_v2s_b32 s63, v145, 0x0
	.loc	1 31 36                         ; candidate.py:31:36
	sl_and_b32 {s10, wcr}, s2, 0x20000
	sl_add_i64 s[2:3], s[10:11], s[48:49]
	.loc	1 30 18                         ; candidate.py:30:18
	sl_wait vmcnt(1)
	ml_mov_v2s_b32 s60, v146, 0x0
	ml_mov_v2s_b32 s61, v147, 0x0
	.loc	1 31 36                         ; candidate.py:31:36
	sl_srl_b32 {s10, wcr}, s47, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	.loc	1 30 18                         ; candidate.py:30:18
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s4, v148, 0x0
	ml_mov_v2s_b32 s5, v149, 0x0
	.loc	1 31 36                         ; candidate.py:31:36
	sl_add_i64 s[12:13], s[10:11], s[46:47]
	sl_srl_b32 {s10, wcr}, s35, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[14:15], s[10:11], s[34:35]
	sl_srl_b32 {s10, wcr}, s23, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[16:17], s[10:11], s[22:23]
	sl_srl_b32 {s10, wcr}, s65, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[18:19], s[10:11], s[64:65]
	sl_srl_b32 {s10, wcr}, s21, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[20:21], s[10:11], s[20:21]
	sl_srl_b32 {s10, wcr}, s51, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[22:23], s[10:11], s[50:51]
	sl_srl_b32 {s10, wcr}, s77, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[24:25], s[10:11], s[76:77]
	sl_srl_b32 {s10, wcr}, s45, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[34:35], s[10:11], s[44:45]
	sl_srl_b32 {s10, wcr}, s67, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[36:37], s[10:11], s[66:67]
	sl_srl_b32 {s10, wcr}, s39, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[38:39], s[10:11], s[38:39]
	sl_srl_b32 {s10, wcr}, s33, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[40:41], s[10:11], s[32:33]
	sl_srl_b32 {s10, wcr}, s43, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[42:43], s[10:11], s[42:43]
	sl_srl_b32 {s10, wcr}, s89, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[44:45], s[10:11], s[88:89]
	sl_srl_b32 {s10, wcr}, s69, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[46:47], s[10:11], s[68:69]
	sl_srl_b32 {s10, wcr}, s81, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[48:49], s[10:11], s[80:81]
	sl_srl_b32 {s10, wcr}, s87, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[50:51], s[10:11], s[86:87]
	sl_srl_b32 {s10, wcr}, s53, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[52:53], s[10:11], s[52:53]
	sl_srl_b32 {s10, wcr}, s55, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[54:55], s[10:11], s[54:55]
	sl_srl_b32 {s10, wcr}, s57, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[56:57], s[10:11], s[56:57]
	sl_srl_b32 {s10, wcr}, s59, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[58:59], s[10:11], s[58:59]
	sl_srl_b32 {s10, wcr}, s91, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[26:27], s[10:11], s[90:91]
	sl_srl_b32 {s10, wcr}, s7, 0xe
	sl_and_b32 {s10, wcr}, s10, 0x20000
	sl_add_i64 s[32:33], s[10:11], s[6:7]
	sl_srl_b32 {s6, wcr}, s85, 0xe
	sl_and_b32 {s10, wcr}, s6, 0x20000
	sl_add_i64 s[68:69], s[10:11], s[84:85]
	sl_srl_b32 {s6, wcr}, s93, 0xe
	sl_and_b32 {s10, wcr}, s6, 0x20000
	sl_add_i64 s[72:73], s[10:11], s[92:93]
	sl_srl_b32 {s6, wcr}, s83, 0xe
	sl_and_b32 {s10, wcr}, s6, 0x20000
	sl_add_i64 s[80:81], s[10:11], s[82:83]
	sl_srl_b32 {s6, wcr}, s31, 0xe
	sl_and_b32 {s10, wcr}, s6, 0x20000
	sl_add_i64 s[82:83], s[10:11], s[30:31]
	sl_srl_b32 {s6, wcr}, s63, 0xe
	sl_and_b32 {s10, wcr}, s6, 0x20000
	sl_add_i64 s[92:93], s[10:11], s[62:63]
	sl_srl_b32 {s6, wcr}, s61, 0xe
	sl_and_b32 {s10, wcr}, s6, 0x20000
	sl_add_i64 s[6:7], s[10:11], s[60:61]
	ml_mov_s2v_b32 v243, s6, 0x24
	ml_mov_s2v_b32 v243, s7, 0x25
	sl_srl_b32 {s6, wcr}, s5, 0xe
	sl_and_b32 {s10, wcr}, s6, 0x20000
	sl_add_i64 s[10:11], s[10:11], s[4:5]
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[4:5], wcr}, s[28:29], 0x8
	sl_add_i64 s[4:5], s[70:71], s[4:5]
	.loc	1 33 23 is_stmt 0               ; candidate.py:33:23
	sl_mov_b32 s7, 0xfff00004
	ml_and_b32 v147, tid, 0x1f
	ml_lsa_load_dword v143, s[4:7], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x8
	sl_add_i64 s[60:61], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	sl_mov_b64 s[62:63], s[6:7]
	ml_mov_s2v_b32 v242, s60, 0x32
	ml_mov_s2v_b32 v242, s61, 0x33
	ml_mov_s2v_b32 v242, s62, 0x34
	ml_mov_s2v_b32 v242, s63, 0x35
	ml_lsa_load_dword v144, s[60:63], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[2:3], 0x8
	sl_add_i64 s[0:1], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	sl_mov_b64 s[2:3], s[6:7]
	ml_mov_s2v_b32 v242, s0, 0x36
	ml_mov_s2v_b32 v242, s1, 0x37
	ml_mov_s2v_b32 v242, s2, 0x38
	ml_mov_s2v_b32 v242, s3, 0x39
	ml_lsa_load_dword v145, s[0:3], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[12:13], 0x8
	sl_add_i64 s[0:1], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_mov_s2v_b32 v242, s0, 0x3a
	ml_mov_s2v_b32 v242, s1, 0x3b
	ml_mov_s2v_b32 v242, s2, 0x3c
	ml_mov_s2v_b32 v242, s3, 0x3d
	ml_lsa_load_dword v146, s[0:3], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[14:15], 0x8
	sl_add_i64 s[0:1], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_mov_s2v_b32 v242, s0, 0x3e
	ml_mov_s2v_b32 v242, s1, 0x3f
	ml_mov_s2v_b32 v243, s2, 0x0
	ml_mov_s2v_b32 v243, s3, 0x1
	ml_lsa_load_dword v148, s[0:3], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[16:17], 0x8
	sl_add_i64 s[0:1], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_mov_s2v_b32 v243, s0, 0x2
	ml_mov_s2v_b32 v243, s1, 0x3
	ml_mov_s2v_b32 v243, s2, 0x4
	ml_mov_s2v_b32 v243, s3, 0x5
	ml_lsa_load_dword v149, s[0:3], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[18:19], 0x8
	sl_add_i64 s[0:1], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_mov_s2v_b32 v243, s0, 0x6
	ml_mov_s2v_b32 v243, s1, 0x7
	ml_mov_s2v_b32 v243, s2, 0x8
	ml_mov_s2v_b32 v243, s3, 0x9
	ml_lsa_load_dword v150, s[0:3], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[20:21], 0x8
	sl_add_i64 s[0:1], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_mov_s2v_b32 v243, s0, 0xa
	ml_mov_s2v_b32 v243, s1, 0xb
	ml_mov_s2v_b32 v243, s2, 0xc
	ml_mov_s2v_b32 v243, s3, 0xd
	ml_lsa_load_dword v151, s[0:3], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[22:23], 0x8
	sl_add_i64 s[0:1], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_mov_s2v_b32 v243, s0, 0xe
	ml_mov_s2v_b32 v243, s1, 0xf
	ml_mov_s2v_b32 v243, s2, 0x10
	ml_mov_s2v_b32 v243, s3, 0x11
	ml_lsa_load_dword v152, s[0:3], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[24:25], 0x8
	sl_add_i64 s[0:1], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_mov_s2v_b32 v243, s0, 0x20
	ml_mov_s2v_b32 v243, s1, 0x21
	ml_mov_s2v_b32 v243, s2, 0x22
	ml_mov_s2v_b32 v243, s3, 0x23
	ml_lsa_load_dword v153, s[0:3], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[34:35], 0x8
	sl_add_i64 s[0:1], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_mov_s2v_b32 v243, s0, 0x1c
	ml_mov_s2v_b32 v243, s1, 0x1d
	ml_mov_s2v_b32 v243, s2, 0x1e
	ml_mov_s2v_b32 v243, s3, 0x1f
	ml_lsa_load_dword v154, s[0:3], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[36:37], 0x8
	sl_add_i64 s[0:1], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_mov_s2v_b32 v243, s0, 0x18
	ml_mov_s2v_b32 v243, s1, 0x19
	ml_mov_s2v_b32 v243, s2, 0x1a
	ml_mov_s2v_b32 v243, s3, 0x1b
	ml_lsa_load_dword v155, s[0:3], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[38:39], 0x8
	sl_add_i64 s[0:1], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_mov_s2v_b32 v243, s0, 0x26
	ml_mov_s2v_b32 v243, s1, 0x27
	ml_mov_s2v_b32 v243, s2, 0x28
	ml_mov_s2v_b32 v243, s3, 0x29
	ml_lsa_load_dword v156, s[0:3], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[40:41], 0x8
	sl_add_i64 s[20:21], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	sl_mov_b64 s[22:23], s[6:7]
	ml_lsa_load_dword v157, s[20:23], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[42:43], 0x8
	sl_add_i64 s[28:29], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	sl_mov_b64 s[30:31], s[6:7]
	ml_lsa_load_dword v158, s[28:31], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[44:45], 0x8
	sl_add_i64 s[60:61], s[70:71], s[0:1]
	sl_shl_b64 {s[0:1], wcr}, s[46:47], 0x8
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v159, s[60:63], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_add_i64 s[64:65], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	sl_mov_b64 s[66:67], s[6:7]
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[48:49], 0x8
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v160, s[64:67], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_add_i64 s[40:41], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	sl_mov_b64 s[42:43], s[6:7]
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[50:51], 0x8
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v161, s[40:43], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_add_i64 s[84:85], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	sl_mov_b64 s[86:87], s[6:7]
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[52:53], 0x8
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v162, s[84:87], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_add_i64 s[88:89], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	sl_mov_b64 s[90:91], s[6:7]
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[54:55], 0x8
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v163, s[88:91], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_add_i64 s[44:45], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	sl_mov_b64 s[46:47], s[6:7]
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[56:57], 0x8
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v164, s[44:47], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_add_i64 s[52:53], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	sl_mov_b64 s[54:55], s[6:7]
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[58:59], 0x8
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v165, s[52:55], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_add_i64 s[12:13], s[70:71], s[0:1]
	.loc	1 33 23                         ; candidate.py:33:23
	sl_mov_b64 s[14:15], s[6:7]
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[0:1], wcr}, s[26:27], 0x8
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v166, s[12:15], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_add_i64 s[0:1], s[70:71], s[0:1]
	sl_shl_b64 {s[16:17], wcr}, s[32:33], 0x8
	sl_add_i64 s[16:17], s[70:71], s[16:17]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v167, s[0:3], unsigned v147, noreg, #0, ca|mie
	sl_mov_b64 s[18:19], s[6:7]
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[24:25], wcr}, s[68:69], 0x8
	sl_add_i64 s[48:49], s[70:71], s[24:25]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v168, s[16:19], unsigned v147, noreg, #0, ca|mie
	sl_mov_b64 s[50:51], s[6:7]
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[24:25], wcr}, s[72:73], 0x8
	sl_add_i64 s[56:57], s[70:71], s[24:25]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v169, s[48:51], unsigned v147, noreg, #0, ca|mie
	sl_mov_b64 s[58:59], s[6:7]
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[24:25], wcr}, s[80:81], 0x8
	sl_add_i64 s[72:73], s[70:71], s[24:25]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v170, s[56:59], unsigned v147, noreg, #0, ca|mie
	sl_mov_b64 s[74:75], s[6:7]
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[24:25], wcr}, s[82:83], 0x8
	sl_add_i64 s[76:77], s[70:71], s[24:25]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v171, s[72:75], unsigned v147, noreg, #0, ca|mie
	sl_mov_b64 s[78:79], s[6:7]
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[24:25], wcr}, s[92:93], 0x8
	sl_add_i64 s[80:81], s[70:71], s[24:25]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v172, s[76:79], unsigned v147, noreg, #0, ca|mie
	sl_mov_b64 s[82:83], s[6:7]
	.loc	1 33 29                         ; candidate.py:33:29
	ml_mov_v2s_b32 s24, v243, 0x24
	ml_mov_v2s_b32 s25, v243, 0x25
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v173, s[80:83], unsigned v147, noreg, #0, ca|mie
	sl_mov_b64 s[38:39], s[6:7]
	.loc	1 33 29                         ; candidate.py:33:29
	sl_shl_b64 {s[10:11], wcr}, s[10:11], 0x8
	sl_shl_b64 {s[24:25], wcr}, s[24:25], 0x8
	sl_add_i64 s[36:37], s[70:71], s[24:25]
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v174, s[36:39], unsigned v147, noreg, #0, ca|mie
	.loc	1 33 29                         ; candidate.py:33:29
	sl_add_i64 s[24:25], s[70:71], s[10:11]
	.loc	1 33 23                         ; candidate.py:33:23
	sl_mov_b64 s[26:27], s[6:7]
	.loc	1 29 27 is_stmt 1               ; candidate.py:29:27
	ml_shl_b32 v136, v3, 0x10
	.loc	1 33 23                         ; candidate.py:33:23
	ml_lsa_load_dword v175, s[24:27], unsigned v147, noreg, #0, ca|mie
	.loc	1 29 27                         ; candidate.py:29:27
	ml_shl_b32 v138, v8, 0x10
	ml_shl_b32 v137, v4, 0x10
	ml_shl_b32 v3, v5, 0x10
	ml_shl_b32 v4, v6, 0x10
	ml_shl_b32 v8, v12, 0x10
	ml_shl_b32 v5, v7, 0x10
	ml_shl_b32 v7, v13, 0x10
	ml_shl_b32 v6, v9, 0x10
	.loc	1 33 65                         ; candidate.py:33:65
	sl_wait vmcnt(0) lmcnt(0)
	sl_barrier 
	ml_shl_b32 v9, v129, 0xb
	ml_or_b32 v9, v127, v9
	ml_byte_permute_b32 v139, v144, v143, tcr_lo
	ml_byte_permute_b32 v140, v153, v152, tcr_lo
	ml_byte_permute_b32 v141, v161, v160, tcr_lo
	ml_byte_permute_b32 v142, v169, v168, tcr_lo
	ml_slb_store_b32x4  v[139:142], v9, noreg, #0, null
	sl_mov_b32 s6, 0x3020706
	ml_byte_permute_b32 v140, v153, v152, s6
	ml_byte_permute_b32 v139, v144, v143, s6
	ml_byte_permute_b32 v142, v169, v168, s6
	ml_byte_permute_b32 v141, v161, v160, s6
	sl_mov_b32 s34, 0x8000
	ml_slb_store_b32x4  v[139:142], v9, s34, #0, null
	sl_mov_b32 s10, 0x400
	ml_byte_permute_b32 v139, v146, v145, tcr_lo
	ml_byte_permute_b32 v140, v155, v154, tcr_lo
	ml_byte_permute_b32 v141, v163, v162, tcr_lo
	ml_byte_permute_b32 v142, v171, v170, tcr_lo
	ml_slb_store_b32x4  v[139:142], v9, s10, #0, null
	sl_mov_b32 s11, 0x8400
	ml_byte_permute_b32 v140, v155, v154, s6
	ml_byte_permute_b32 v139, v146, v145, s6
	ml_byte_permute_b32 v142, v171, v170, s6
	ml_byte_permute_b32 v141, v163, v162, s6
	ml_slb_store_b32x4  v[139:142], v9, s11, #0, null
	sl_mov_b32 s10, 0x800
	ml_byte_permute_b32 v139, v149, v148, tcr_lo
	ml_byte_permute_b32 v140, v157, v156, tcr_lo
	ml_byte_permute_b32 v141, v165, v164, tcr_lo
	ml_byte_permute_b32 v142, v173, v172, tcr_lo
	ml_slb_store_b32x4  v[139:142], v9, s10, #0, null
	sl_mov_b32 s10, 0x8800
	ml_byte_permute_b32 v140, v157, v156, s6
	ml_byte_permute_b32 v139, v149, v148, s6
	ml_byte_permute_b32 v142, v173, v172, s6
	ml_byte_permute_b32 v141, v165, v164, s6
	ml_slb_store_b32x4  v[139:142], v9, s10, #0, null
	sl_mov_b32 s35, 0xc00
	ml_byte_permute_b32 v139, v151, v150, tcr_lo
	ml_byte_permute_b32 v140, v159, v158, tcr_lo
	ml_byte_permute_b32 v141, v167, v166, tcr_lo
	ml_byte_permute_b32 v142, v175, v174, tcr_lo
	ml_slb_store_b32x4  v[139:142], v9, s35, #0, null
	sl_mov_b32 s35, 0x8c00
	ml_byte_permute_b32 v140, v159, v158, s6
	ml_byte_permute_b32 v139, v151, v150, s6
	ml_byte_permute_b32 v142, v175, v174, s6
	ml_byte_permute_b32 v141, v167, v166, s6
	ml_slb_store_b32x4  v[139:142], v9, s35, #0, null
	sl_wait lmcnt(0)
	sl_barrier 
	.loc	1 34 21                         ; candidate.py:34:21
	ml_lsa_load_dword v127, s[4:7], unsigned v147, noreg, #128, ca|mie
	ml_mov_v2s_b32 s4, v242, 0x32
	ml_mov_v2s_b32 s5, v242, 0x33
	ml_mov_v2s_b32 s6, v242, 0x34
	ml_mov_v2s_b32 s7, v242, 0x35
	ml_lsa_load_dword v166, s[20:23], unsigned v147, noreg, #128, ca|mie
	.loc	1 33 65                         ; candidate.py:33:65
	ml_add_i32 v15, v14, v15
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v92, 0x10
	ml_shl_b32 v95, v95, 0x10
	.loc	1 34 21                         ; candidate.py:34:21
	ml_lsa_load_dword v129, s[4:7], unsigned v147, noreg, #128, ca|mie
	ml_mov_v2s_b32 s4, v242, 0x36
	ml_mov_v2s_b32 s5, v242, 0x37
	ml_mov_v2s_b32 s6, v242, 0x38
	ml_mov_v2s_b32 s7, v242, 0x39
	ml_lsa_load_dword v167, s[28:31], unsigned v147, noreg, #128, ca|mie
	ml_lsa_load_dword v155, s[4:7], unsigned v147, noreg, #128, ca|mie
	ml_mov_v2s_b32 s4, v242, 0x3a
	ml_mov_v2s_b32 s5, v242, 0x3b
	ml_mov_v2s_b32 s6, v242, 0x3c
	ml_mov_v2s_b32 s7, v242, 0x3d
	ml_lsa_load_dword v168, s[60:63], unsigned v147, noreg, #128, ca|mie
	ml_lsa_load_dword v156, s[4:7], unsigned v147, noreg, #128, ca|mie
	ml_mov_v2s_b32 s4, v242, 0x3e
	ml_mov_v2s_b32 s5, v242, 0x3f
	ml_mov_v2s_b32 s6, v243, 0x0
	ml_mov_v2s_b32 s7, v243, 0x1
	ml_lsa_load_dword v169, s[64:67], unsigned v147, noreg, #128, ca|mie
	ml_lsa_load_dword v157, s[4:7], unsigned v147, noreg, #128, ca|mie
	ml_mov_v2s_b32 s4, v243, 0x2
	ml_mov_v2s_b32 s5, v243, 0x3
	ml_mov_v2s_b32 s6, v243, 0x4
	ml_mov_v2s_b32 s7, v243, 0x5
	ml_lsa_load_dword v170, s[40:43], unsigned v147, noreg, #128, ca|mie
	ml_mov_v2s_b32 s43, v243, 0x16
	ml_lsa_load_dword v158, s[4:7], unsigned v147, noreg, #128, ca|mie
	ml_mov_v2s_b32 s4, v243, 0x6
	ml_mov_v2s_b32 s5, v243, 0x7
	ml_mov_v2s_b32 s6, v243, 0x8
	ml_mov_v2s_b32 s7, v243, 0x9
	ml_lsa_load_dword v171, s[84:87], unsigned v147, noreg, #128, ca|mie
	ml_lsa_load_dword v159, s[4:7], unsigned v147, noreg, #128, ca|mie
	ml_mov_v2s_b32 s4, v243, 0xa
	ml_mov_v2s_b32 s5, v243, 0xb
	ml_mov_v2s_b32 s6, v243, 0xc
	ml_mov_v2s_b32 s7, v243, 0xd
	ml_lsa_load_dword v172, s[88:91], unsigned v147, noreg, #128, ca|mie
	ml_lsa_load_dword v160, s[4:7], unsigned v147, noreg, #128, ca|mie
	ml_mov_v2s_b32 s4, v243, 0xe
	ml_mov_v2s_b32 s5, v243, 0xf
	ml_mov_v2s_b32 s6, v243, 0x10
	ml_mov_v2s_b32 s7, v243, 0x11
	ml_lsa_load_dword v173, s[44:47], unsigned v147, noreg, #128, ca|mie
	ml_mov_v2s_b32 s44, v243, 0x12
	ml_lsa_load_dword v161, s[4:7], unsigned v147, noreg, #128, ca|mie
	ml_mov_v2s_b32 s4, v243, 0x20
	ml_mov_v2s_b32 s5, v243, 0x21
	ml_mov_v2s_b32 s6, v243, 0x22
	ml_mov_v2s_b32 s7, v243, 0x23
	ml_lsa_load_dword v174, s[52:55], unsigned v147, noreg, #128, ca|mie
	ml_lsa_load_dword v162, s[4:7], unsigned v147, noreg, #128, ca|mie
	ml_mov_v2s_b32 s4, v243, 0x1c
	ml_mov_v2s_b32 s5, v243, 0x1d
	ml_mov_v2s_b32 s6, v243, 0x1e
	ml_mov_v2s_b32 s7, v243, 0x1f
	ml_lsa_load_dword v175, s[12:15], unsigned v147, noreg, #128, ca|mie
	ml_lsa_load_dword v163, s[4:7], unsigned v147, noreg, #128, ca|mie
	ml_mov_v2s_b32 s4, v243, 0x18
	ml_mov_v2s_b32 s5, v243, 0x19
	ml_mov_v2s_b32 s6, v243, 0x1a
	ml_mov_v2s_b32 s7, v243, 0x1b
	ml_lsa_load_dword v176, s[0:3], unsigned v147, noreg, #128, ca|mie
	.loc	1 33 65                         ; candidate.py:33:65
	ml_mov_v2s_b32 s0, v242, 0x2e
	.loc	1 34 21                         ; candidate.py:34:21
	ml_lsa_load_dword v164, s[4:7], unsigned v147, noreg, #128, ca|mie
	ml_mov_v2s_b32 s4, v243, 0x26
	ml_mov_v2s_b32 s5, v243, 0x27
	ml_mov_v2s_b32 s6, v243, 0x28
	ml_mov_v2s_b32 s7, v243, 0x29
	ml_lsa_load_dword v177, s[16:19], unsigned v147, noreg, #128, ca|mie
	.loc	1 33 65                         ; candidate.py:33:65
	sl_mull_u32 s1, s0, 0x100
	sl_add_i32 s0, s1, 0x1000
	sl_add_i32 s3, s1, 0x2000
	.loc	1 34 21                         ; candidate.py:34:21
	ml_lsa_load_dword v165, s[4:7], unsigned v147, noreg, #128, ca|mie
	.loc	1 33 65                         ; candidate.py:33:65
	sl_add_i32 s2, s1, 0x3000
	.loc	1 34 21                         ; candidate.py:34:21
	ml_lsa_load_dword v178, s[48:51], unsigned v147, noreg, #128, ca|mie
	ml_lsa_load_dword v179, s[56:59], unsigned v147, noreg, #128, ca|mie
	ml_lsa_load_dword v180, s[72:75], unsigned v147, noreg, #128, ca|mie
	ml_lsa_load_dword v181, s[76:79], unsigned v147, noreg, #128, ca|mie
	ml_lsa_load_dword v182, s[80:83], unsigned v147, noreg, #128, ca|mie
	.loc	1 33 65                         ; candidate.py:33:65
	ml_slb_load_b32x4  v[139:142], v15, s1, #0, null
	ml_slb_load_b32x4  v[143:146], v15, s1, #512, null
	.loc	1 34 21                         ; candidate.py:34:21
	ml_lsa_load_dword v183, s[36:39], unsigned v147, noreg, #128, ca|mie
	ml_lsa_load_dword v184, s[24:27], unsigned v147, noreg, #128, ca|mie
	.loc	1 33 65                         ; candidate.py:33:65
	ml_slb_load_b32x4  v[147:150], v15, s0, #0, null
	sl_wait lmcnt(2)
	ml_shl_b32 v12, v139, 0x10
	ml_and_b32 v14, v139, 0xffff0000
	ml_shl_b32 v186, v140, 0x10
	ml_slb_load_b32x4  v[151:154], v15, s0, #512, null
	sl_wait lmcnt(2)
	ml_shl_b32 v13, v143, 0x10
	ml_and_b32 v185, v143, 0xffff0000
	ml_shl_b32 v187, v144, 0x10
	ml_and_b32 v188, v140, 0xffff0000
	ml_and_b32 v189, v144, 0xffff0000
	ml_shl_b32 v190, v141, 0x10
	ml_shl_b32 v191, v145, 0x10
	ml_and_b32 v192, v141, 0xffff0000
	ml_and_b32 v193, v145, 0xffff0000
	ml_shl_b32 v194, v142, 0x10
	ml_shl_b32 v195, v146, 0x10
	ml_and_b32 v196, v142, 0xffff0000
	ml_and_b32 v197, v146, 0xffff0000
	sl_wait lmcnt(1)
	ml_shl_b32 v198, v147, 0x10
	ml_and_b32 v200, v147, 0xffff0000
	ml_slb_load_b32x4  v[139:142], v15, s3, #0, null
	ml_shl_b32 v202, v148, 0x10
	ml_and_b32 v204, v148, 0xffff0000
	ml_shl_b32 v206, v149, 0x10
	sl_wait lmcnt(1)
	ml_shl_b32 v199, v151, 0x10
	ml_and_b32 v201, v151, 0xffff0000
	ml_shl_b32 v203, v152, 0x10
	ml_slb_load_b32x4  v[143:146], v15, s3, #512, null
	ml_and_b32 v205, v152, 0xffff0000
	ml_shl_b32 v207, v153, 0x10
	ml_and_b32 v208, v149, 0xffff0000
	ml_and_b32 v209, v153, 0xffff0000
	ml_shl_b32 v210, v150, 0x10
	ml_shl_b32 v211, v154, 0x10
	ml_and_b32 v212, v150, 0xffff0000
	ml_and_b32 v213, v154, 0xffff0000
	ml_slb_load_b32x4  v[147:150], v15, s2, #0, null
	sl_wait lmcnt(2)
	ml_shl_b32 v214, v139, 0x10
	ml_and_b32 v216, v139, 0xffff0000
	ml_shl_b32 v218, v140, 0x10
	ml_slb_load_b32x4  v[151:154], v15, s2, #512, null
	ml_and_b32 v220, v140, 0xffff0000
	ml_shl_b32 v222, v141, 0x10
	ml_and_b32 v224, v141, 0xffff0000
	sl_wait lmcnt(2)
	ml_shl_b32 v215, v143, 0x10
	ml_and_b32 v217, v143, 0xffff0000
	ml_shl_b32 v219, v144, 0x10
	ml_and_b32 v221, v144, 0xffff0000
	ml_shl_b32 v223, v145, 0x10
	ml_and_b32 v225, v145, 0xffff0000
	ml_shl_b32 v226, v142, 0x10
	ml_shl_b32 v227, v146, 0x10
	ml_and_b32 v228, v142, 0xffff0000
	ml_and_b32 v229, v146, 0xffff0000
	sl_wait lmcnt(1)
	ml_shl_b32 v230, v147, 0x10
	ml_and_b32 v232, v147, 0xffff0000
	ml_shl_b32 v233, v148, 0x10
	ml_and_b32 v235, v148, 0xffff0000
	ml_shl_b32 v236, v149, 0x10
	ml_and_b32 v238, v149, 0xffff0000
	sl_wait lmcnt(0)
	ml_shl_b32 v231, v151, 0x10
	ml_and_b32 v151, v151, 0xffff0000
	ml_shl_b32 v234, v152, 0x10
	ml_and_b32 v152, v152, 0xffff0000
	ml_shl_b32 v237, v153, 0x10
	ml_and_b32 v153, v153, 0xffff0000
	ml_shl_b32 v239, v150, 0x10
	ml_shl_b32 v240, v154, 0x10
	ml_and_b32 v241, v150, 0xffff0000
	ml_and_b32 v154, v154, 0xffff0000
	.loc	1 34 66                         ; candidate.py:34:66
	sl_wait vmcnt(31)
	ml_and_b32 v139, v127, 0xffff0000
	sl_wait vmcnt(29)
	ml_and_b32 v140, v129, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v140, v95, v140
	ml_mul_f32 v139, v92, v139
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v96, 0x10
	ml_shl_b32 v95, v97, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	sl_wait vmcnt(27)
	ml_and_b32 v97, v155, 0xffff0000
	sl_wait vmcnt(25)
	ml_and_b32 v96, v156, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v96, v95, v96
	ml_mul_f32 v95, v92, v97
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v98, 0x10
	ml_shl_b32 v97, v99, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	sl_wait vmcnt(23)
	ml_and_b32 v98, v157, 0xffff0000
	sl_wait vmcnt(21)
	ml_and_b32 v99, v158, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v144, v97, v99
	ml_mul_f32 v143, v92, v98
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v100, 0x10
	ml_shl_b32 v97, v103, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	sl_wait vmcnt(19)
	ml_and_b32 v98, v159, 0xffff0000
	sl_wait vmcnt(17)
	ml_and_b32 v99, v160, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v148, v97, v99
	ml_mul_f32 v147, v92, v98
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v106, 0x10
	ml_shl_b32 v97, v111, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	sl_wait vmcnt(15)
	ml_and_b32 v98, v161, 0xffff0000
	sl_wait vmcnt(13)
	ml_and_b32 v99, v162, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v142, v97, v99
	ml_mul_f32 v141, v92, v98
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v112, 0x10
	ml_shl_b32 v97, v113, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	sl_wait vmcnt(11)
	ml_and_b32 v99, v163, 0xffff0000
	sl_wait vmcnt(9)
	ml_and_b32 v98, v164, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v98, v97, v98
	ml_mul_f32 v97, v92, v99
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v114, 0x10
	ml_shl_b32 v99, v115, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	sl_wait vmcnt(7)
	ml_and_b32 v100, v165, 0xffff0000
	ml_and_b32 v103, v166, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v146, v99, v103
	ml_mul_f32 v145, v92, v100
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v116, 0x10
	ml_shl_b32 v99, v117, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	ml_and_b32 v100, v167, 0xffff0000
	ml_and_b32 v103, v168, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v150, v99, v103
	ml_mul_f32 v149, v92, v100
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v118, 0x10
	ml_shl_b32 v99, v119, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	ml_and_b32 v100, v169, 0xffff0000
	ml_and_b32 v103, v170, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v112, v99, v103
	ml_mul_f32 v111, v92, v100
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v120, 0x10
	ml_shl_b32 v99, v121, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	ml_and_b32 v100, v171, 0xffff0000
	ml_and_b32 v103, v172, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v116, v99, v103
	ml_mul_f32 v115, v92, v100
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v122, 0x10
	ml_shl_b32 v99, v123, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	ml_and_b32 v100, v173, 0xffff0000
	ml_and_b32 v103, v174, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v120, v99, v103
	ml_mul_f32 v119, v92, v100
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v124, 0x10
	ml_shl_b32 v99, v125, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	ml_and_b32 v100, v175, 0xffff0000
	ml_and_b32 v103, v176, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v124, v99, v103
	ml_mul_f32 v123, v92, v100
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v126, 0x10
	ml_shl_b32 v99, v128, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	ml_and_b32 v100, v177, 0xffff0000
	sl_wait vmcnt(6)
	ml_and_b32 v103, v178, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v114, v99, v103
	ml_mul_f32 v113, v92, v100
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v130, 0x10
	ml_shl_b32 v99, v131, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	sl_wait vmcnt(5)
	ml_and_b32 v100, v179, 0xffff0000
	sl_wait vmcnt(4)
	ml_and_b32 v103, v180, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v118, v99, v103
	ml_mul_f32 v117, v92, v100
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v132, 0x10
	ml_shl_b32 v99, v133, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	sl_wait vmcnt(3)
	ml_and_b32 v100, v181, 0xffff0000
	sl_wait vmcnt(2)
	ml_and_b32 v103, v182, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v122, v99, v103
	ml_mul_f32 v121, v92, v100
	.loc	1 28 57                         ; candidate.py:28:57
	ml_shl_b32 v92, v134, 0x10
	ml_shl_b32 v99, v135, 0x10
	.loc	1 34 66                         ; candidate.py:34:66
	sl_wait vmcnt(1)
	ml_and_b32 v100, v183, 0xffff0000
	sl_wait vmcnt(0)
	ml_and_b32 v103, v184, 0xffff0000
	.loc	1 36 25                         ; candidate.py:36:25
	ml_mul_f32 v126, v99, v103
	ml_mul_f32 v125, v92, v100
	sl_barrier 
	ml_shl_b32 v70, v70, 0x10
	ml_shl_b32 v75, v75, 0x10
	ml_shl_b32 v85, v85, 0x10
	ml_shl_b32 v90, v90, 0x10
	ml_shl_b32 v92, v127, 0x10
	ml_shl_b32 v99, v129, 0x10
	ml_shl_b32 v100, v161, 0x10
	ml_shl_b32 v103, v162, 0x10
	ml_mul_f32 v130, v90, v103
	ml_mul_f32 v129, v85, v100
	ml_mul_f32 v128, v75, v99
	ml_mul_f32 v127, v70, v92
	ml_slb_store_b32x4  v[127:130], v9, noreg, #0, null
	ml_shl_b32 v70, v71, 0x10
	ml_shl_b32 v71, v74, 0x10
	ml_shl_b32 v74, v87, 0x10
	ml_slb_store_b32x4  v[139:142], v9, s34, #0, null
	ml_shl_b32 v75, v91, 0x10
	ml_shl_b32 v85, v155, 0x10
	ml_shl_b32 v87, v156, 0x10
	ml_shl_b32 v90, v163, 0x10
	ml_shl_b32 v91, v164, 0x10
	ml_mul_f32 v130, v75, v91
	ml_mul_f32 v129, v74, v90
	ml_mul_f32 v128, v71, v87
	ml_mul_f32 v127, v70, v85
	.loc	1 28 37                         ; candidate.py:28:37
	sl_mov_b32 s7, 0x400
	.loc	1 36 25                         ; candidate.py:36:25
	ml_slb_store_b32x4  v[127:130], v9, s7, #0, null
	ml_shl_b32 v70, v72, 0x10
	ml_shl_b32 v71, v76, 0x10
	ml_shl_b32 v72, v88, 0x10
	ml_slb_store_b32x4  v[95:98], v9, s11, #0, null
	ml_shl_b32 v74, v93, 0x10
	ml_shl_b32 v75, v157, 0x10
	ml_shl_b32 v76, v158, 0x10
	ml_shl_b32 v85, v165, 0x10
	ml_shl_b32 v87, v166, 0x10
	ml_mul_f32 v93, v74, v87
	ml_mul_f32 v92, v72, v85
	ml_mul_f32 v91, v71, v76
	ml_mul_f32 v90, v70, v75
	.loc	1 28 37                         ; candidate.py:28:37
	sl_mov_b32 s5, 0x800
	.loc	1 36 25                         ; candidate.py:36:25
	ml_slb_store_b32x4  v[90:93], v9, s5, #0, null
	ml_shl_b32 v70, v73, 0x10
	ml_shl_b32 v71, v77, 0x10
	ml_shl_b32 v72, v89, 0x10
	ml_slb_store_b32x4  v[143:146], v9, s10, #0, null
	ml_shl_b32 v73, v94, 0x10
	ml_shl_b32 v74, v159, 0x10
	ml_shl_b32 v75, v160, 0x10
	ml_shl_b32 v76, v167, 0x10
	ml_shl_b32 v77, v168, 0x10
	ml_mul_f32 v73, v73, v77
	ml_mul_f32 v72, v72, v76
	ml_mul_f32 v71, v71, v75
	ml_mul_f32 v70, v70, v74
	.loc	1 28 37                         ; candidate.py:28:37
	sl_mov_b32 s4, 0xc00
	.loc	1 36 25                         ; candidate.py:36:25
	ml_slb_store_b32x4  v[70:73], v9, s4, #0, null
	ml_slb_store_b32x4  v[147:150], v9, s35, #0, null
	sl_wait lmcnt(0)
	sl_barrier 
	ml_slb_load_b32x4  v[70:73], v15, s1, #0, null
	ml_slb_load_b32x4  v[74:77], v15, s1, #512, null
	ml_slb_load_b32x4  v[87:90], v15, s0, #0, null
	ml_slb_load_b32x4  v[91:94], v15, s0, #512, null
	ml_slb_load_b32x4  v[95:98], v15, s3, #0, null
	ml_slb_load_b32x4  v[127:130], v15, s3, #512, null
	ml_slb_load_b32x4  v[131:134], v15, s2, #0, null
	ml_slb_load_b32x4  v[139:142], v15, s2, #512, null
	sl_wait lmcnt(0)
	sl_barrier 
	ml_shl_b32 v83, v83, 0x10
	ml_shl_b32 v85, v86, 0x10
	ml_shl_b32 v86, v101, 0x10
	ml_shl_b32 v99, v107, 0x10
	ml_shl_b32 v100, v169, 0x10
	ml_shl_b32 v101, v170, 0x10
	ml_shl_b32 v103, v177, 0x10
	ml_shl_b32 v106, v178, 0x10
	ml_mul_f32 v146, v99, v106
	ml_mul_f32 v145, v86, v103
	ml_mul_f32 v144, v85, v101
	ml_mul_f32 v143, v83, v100
	ml_slb_store_b32x4  v[143:146], v9, noreg, #0, null
	ml_shl_b32 v81, v81, 0x10
	ml_shl_b32 v83, v84, 0x10
	ml_shl_b32 v84, v102, 0x10
	ml_slb_store_b32x4  v[111:114], v9, s34, #0, null
	ml_shl_b32 v85, v108, 0x10
	ml_shl_b32 v99, v171, 0x10
	ml_shl_b32 v100, v172, 0x10
	ml_shl_b32 v101, v179, 0x10
	ml_shl_b32 v86, v180, 0x10
	ml_mul_f32 v86, v85, v86
	ml_mul_f32 v85, v84, v101
	ml_mul_f32 v84, v83, v100
	ml_mul_f32 v83, v81, v99
	ml_slb_store_b32x4  v[83:86], v9, s7, #0, null
	ml_shl_b32 v79, v79, 0x10
	ml_shl_b32 v81, v82, 0x10
	ml_shl_b32 v82, v104, 0x10
	ml_slb_store_b32x4  v[115:118], v9, s11, #0, null
	ml_shl_b32 v83, v109, 0x10
	ml_shl_b32 v85, v173, 0x10
	ml_shl_b32 v86, v174, 0x10
	ml_shl_b32 v99, v181, 0x10
	ml_shl_b32 v84, v182, 0x10
	ml_mul_f32 v84, v83, v84
	ml_mul_f32 v83, v82, v99
	ml_mul_f32 v82, v81, v86
	ml_mul_f32 v81, v79, v85
	ml_slb_store_b32x4  v[81:84], v9, s5, #0, null
	ml_shl_b32 v78, v78, 0x10
	ml_shl_b32 v79, v80, 0x10
	ml_shl_b32 v80, v105, 0x10
	ml_slb_store_b32x4  v[119:122], v9, s10, #0, null
	ml_shl_b32 v81, v110, 0x10
	ml_shl_b32 v82, v175, 0x10
	ml_shl_b32 v83, v176, 0x10
	ml_shl_b32 v84, v183, 0x10
	ml_shl_b32 v85, v184, 0x10
	ml_mul_f32 v81, v81, v85
	ml_mul_f32 v80, v80, v84
	ml_mul_f32 v79, v79, v83
	ml_mul_f32 v78, v78, v82
	ml_slb_store_b32x4  v[78:81], v9, s4, #0, null
	ml_slb_store_b32x4  v[123:126], v9, s35, #0, null
	sl_wait lmcnt(0)
	sl_barrier 
	ml_slb_load_b32x4  v[78:81], v15, s3, #0, null
	.loc	1 37 63                         ; candidate.py:37:63
	ml_fma_f32 v63, v63, v214, v95
	ml_fma_f32 v65, v65, v216, v96
	ml_fma_f32 v95, v66, v218, v97
	.loc	1 36 25                         ; candidate.py:36:25
	ml_slb_load_b32x4  v[82:85], v15, s3, #512, null
	ml_mov_v2s_b32 s3, v243, 0x14
	.loc	1 37 63                         ; candidate.py:37:63
	ml_fma_f32 v96, v68, v220, v98
	ml_fma_f32 v68, v50, v215, v127
	ml_fma_f32 v97, v52, v217, v128
	ml_fma_f32 v98, v55, v219, v129
	ml_fma_f32 v99, v58, v221, v130
	ml_fma_f32 v111, v57, v230, v131
	ml_fma_f32 v112, v59, v232, v132
	ml_fma_f32 v62, v62, v233, v133
	ml_fma_f32 v113, v138, v235, v134
	ml_fma_f32 v114, v48, v231, v139
	ml_fma_f32 v115, v49, v151, v140
	ml_fma_f32 v116, v136, v234, v141
	ml_fma_f32 v127, v137, v152, v142
	.loc	1 37 48 is_stmt 0               ; candidate.py:37:48
	ml_xor_b32 v66, v77, 0x80000000
	.loc	1 37 63                         ; candidate.py:37:63
	sl_wait lmcnt(1)
	ml_fma_f32 v100, v60, v222, v78
	ml_fma_f32 v101, v61, v224, v79
	ml_fma_f32 v80, v67, v226, v80
	ml_fma_f32 v103, v69, v228, v81
	sl_wait lmcnt(0)
	ml_fma_f32 v67, v51, v223, v82
	ml_fma_f32 v69, v53, v225, v83
	ml_fma_f32 v106, v54, v227, v84
	.loc	1 36 25 is_stmt 1               ; candidate.py:36:25
	ml_slb_load_b32x4  v[50:53], v15, s2, #0, null
	.loc	1 37 63                         ; candidate.py:37:63
	ml_fma_f32 v85, v56, v229, v85
	.loc	1 37 48 is_stmt 0               ; candidate.py:37:48
	ml_xor_b32 v77, v94, 0x80000000
	ml_fma_f32 v39, v39, v205, v77
	.loc	1 36 25 is_stmt 1               ; candidate.py:36:25
	ml_slb_load_b32x4  v[54:57], v15, s2, #512, null
	ml_mov_v2s_b32 s2, v242, 0x30
	.loc	1 38 29                         ; candidate.py:38:29
	ml_cvt_bf16_f32  v78, v39
	ml_cvt_bf16_f32  v82, v96
	.loc	1 36 25                         ; candidate.py:36:25
	ml_slb_load_b32x4  v[58:61], v15, s1, #0, null
	.loc	1 38 29                         ; candidate.py:38:29
	ml_cvt_bf16_f32  v102, v100
	ml_cvt_bf16_f32  v67, v67
	ml_cvt_bf16_f32  v104, v101
	ml_cvt_bf16_f32  v69, v69
	ml_cvt_bf16_f32  v107, v80
	ml_cvt_bf16_f32  v109, v103
	ml_cvt_bf16_f32  v80, v85
	ml_cvt_bf16_f32  v101, v62
	.loc	1 37 63                         ; candidate.py:37:63
	sl_wait lmcnt(2)
	ml_fma_f32 v129, v10, v236, v50
	ml_fma_f32 v11, v11, v238, v51
	.loc	1 36 25                         ; candidate.py:36:25
	ml_slb_load_b32x4  v[48:51], v15, s1, #512, null
	.loc	1 37 63                         ; candidate.py:37:63
	ml_fma_f32 v136, v8, v239, v52
	ml_fma_f32 v137, v7, v241, v53
	sl_wait lmcnt(2)
	ml_fma_f32 v138, v3, v237, v54
	.loc	1 36 25                         ; candidate.py:36:25
	ml_slb_load_b32x4  v[7:10], v15, s0, #0, null
	.loc	1 37 63                         ; candidate.py:37:63
	ml_fma_f32 v139, v4, v153, v55
	ml_fma_f32 v140, v5, v240, v56
	ml_fma_f32 v141, v6, v154, v57
	.loc	1 36 25                         ; candidate.py:36:25
	ml_slb_load_b32x4  v[3:6], v15, s0, #512, null
	.loc	1 37 48                         ; candidate.py:37:48
	ml_xor_b32 v15, v70, 0x80000000
	ml_xor_b32 v52, v71, 0x80000000
	ml_xor_b32 v53, v72, 0x80000000
	ml_xor_b32 v54, v73, 0x80000000
	ml_xor_b32 v55, v74, 0x80000000
	ml_xor_b32 v56, v75, 0x80000000
	ml_xor_b32 v57, v76, 0x80000000
	sl_wait lmcnt(3)
	ml_xor_b32 v58, v58, 0x80000000
	ml_xor_b32 v59, v59, 0x80000000
	ml_xor_b32 v60, v60, 0x80000000
	ml_xor_b32 v61, v61, 0x80000000
	sl_wait lmcnt(2)
	ml_xor_b32 v48, v48, 0x80000000
	ml_xor_b32 v49, v49, 0x80000000
	ml_xor_b32 v50, v50, 0x80000000
	ml_xor_b32 v51, v51, 0x80000000
	ml_xor_b32 v70, v87, 0x80000000
	ml_xor_b32 v71, v88, 0x80000000
	ml_xor_b32 v72, v89, 0x80000000
	ml_xor_b32 v73, v90, 0x80000000
	ml_xor_b32 v74, v91, 0x80000000
	ml_xor_b32 v75, v92, 0x80000000
	ml_xor_b32 v76, v93, 0x80000000
	sl_wait lmcnt(1)
	ml_xor_b32 v7, v7, 0x80000000
	ml_xor_b32 v8, v8, 0x80000000
	ml_xor_b32 v9, v9, 0x80000000
	ml_xor_b32 v10, v10, 0x80000000
	sl_wait lmcnt(0)
	ml_xor_b32 v3, v3, 0x80000000
	ml_xor_b32 v4, v4, 0x80000000
	ml_xor_b32 v5, v5, 0x80000000
	ml_xor_b32 v6, v6, 0x80000000
	ml_fma_f32 v12, v16, v12, v15
	ml_fma_f32 v13, v17, v13, v55
	ml_fma_f32 v14, v18, v14, v52
	ml_fma_f32 v15, v19, v185, v56
	ml_fma_f32 v16, v20, v186, v53
	ml_fma_f32 v17, v21, v187, v57
	ml_fma_f32 v18, v22, v188, v54
	ml_fma_f32 v19, v23, v189, v66
	ml_fma_f32 v20, v24, v190, v58
	ml_fma_f32 v21, v25, v191, v48
	ml_fma_f32 v22, v26, v192, v59
	ml_fma_f32 v23, v27, v193, v49
	ml_fma_f32 v24, v28, v194, v60
	ml_fma_f32 v25, v29, v195, v50
	ml_fma_f32 v26, v30, v196, v61
	ml_fma_f32 v27, v31, v197, v51
	ml_fma_f32 v28, v32, v198, v70
	ml_fma_f32 v29, v33, v199, v74
	ml_fma_f32 v30, v34, v200, v71
	ml_fma_f32 v31, v35, v201, v75
	ml_fma_f32 v36, v36, v202, v72
	ml_fma_f32 v37, v37, v203, v76
	ml_fma_f32 v38, v38, v204, v73
	ml_fma_f32 v7, v40, v206, v7
	ml_fma_f32 v3, v41, v207, v3
	ml_fma_f32 v8, v42, v208, v8
	ml_fma_f32 v4, v43, v209, v4
	ml_fma_f32 v9, v44, v210, v9
	ml_fma_f32 v5, v45, v211, v5
	ml_fma_f32 v10, v46, v212, v10
	ml_fma_f32 v6, v47, v213, v6
	.loc	1 38 29                         ; candidate.py:38:29
	ml_cvt_bf16_f32  v94, v12
	ml_cvt_bf16_f32  v81, v13
	ml_cvt_bf16_f32  v117, v14
	ml_cvt_bf16_f32  v83, v15
	ml_cvt_bf16_f32  v126, v16
	ml_cvt_bf16_f32  v86, v17
	ml_cvt_bf16_f32  v131, v18
	ml_cvt_bf16_f32  v118, v19
	ml_cvt_bf16_f32  v132, v20
	ml_cvt_bf16_f32  v119, v21
	ml_cvt_bf16_f32  v133, v22
	ml_cvt_bf16_f32  v122, v23
	ml_cvt_bf16_f32  v134, v24
	ml_cvt_bf16_f32  v124, v25
	ml_cvt_bf16_f32  v135, v26
	ml_cvt_bf16_f32  v128, v27
	ml_cvt_bf16_f32  v32, v28
	ml_cvt_bf16_f32  v33, v29
	ml_cvt_bf16_f32  v34, v30
	ml_cvt_bf16_f32  v35, v31
	ml_cvt_bf16_f32  v110, v36
	ml_cvt_bf16_f32  v66, v37
	ml_cvt_bf16_f32  v120, v38
	ml_cvt_bf16_f32  v121, v7
	ml_cvt_bf16_f32  v79, v3
	ml_cvt_bf16_f32  v123, v8
	ml_cvt_bf16_f32  v84, v4
	ml_cvt_bf16_f32  v125, v9
	ml_cvt_bf16_f32  v105, v5
	ml_cvt_bf16_f32  v130, v10
	ml_cvt_bf16_f32  v108, v6
	ml_cvt_bf16_f32  v52, v63
	ml_cvt_bf16_f32  v50, v68
	ml_cvt_bf16_f32  v55, v65
	ml_cvt_bf16_f32  v51, v97
	ml_cvt_bf16_f32  v68, v95
	ml_cvt_bf16_f32  v53, v98
	ml_cvt_bf16_f32  v54, v99
	ml_cvt_bf16_f32  v56, v106
	ml_cvt_bf16_f32  v57, v111
	ml_cvt_bf16_f32  v48, v114
	ml_cvt_bf16_f32  v59, v112
	ml_cvt_bf16_f32  v49, v115
	ml_cvt_bf16_f32  v3, v116
	ml_cvt_bf16_f32  v8, v113
	ml_cvt_bf16_f32  v4, v127
	ml_cvt_bf16_f32  v10, v129
	ml_cvt_bf16_f32  v5, v138
	ml_cvt_bf16_f32  v11, v11
	ml_cvt_bf16_f32  v6, v139
	ml_cvt_bf16_f32  v12, v136
	ml_cvt_bf16_f32  v7, v140
	ml_cvt_bf16_f32  v13, v137
	ml_cvt_bf16_f32  v9, v141
	sl_jump BB0_5
BB0_4:                                  ; %._crit_edge
	.loc	1 25 7                          ; candidate.py:25:7
	ml_shl_b32 v1, v64, 0x8
	ml_and_b32 v1, v1, 0x3000
	ml_and_b32 v2, v65, 0x70
	sl_mull_u32 s3, s1, 0x2
BB0_5:
	.loc	1 13 12                         ; candidate.py:13:12
	sl_mull_u32 s0, s43, 0x80
	.loc	1 13 27 is_stmt 0               ; candidate.py:13:27
	ml_shl_b32 v14, tid, 0x1
	.loc	1 13 15                         ; candidate.py:13:15
	ml_add_i32 v36, s0, v14
	.loc	1 25 7 is_stmt 1                ; candidate.py:25:7
	sl_barrier 
	ml_shl_b32 v14, v64, 0xe
	sl_mull_u32 s0, s44, 0x200
	sl_and_b32 {s0, wcr}, s0, 0x8000
	sl_mov_b32 s72, 0x1000504
	sl_mov_b32 s1, 0x4000
	ml_anyop3_b32 v0, v0, v14, s1, 0xffffffea
	ml_byte_permute_b32 v17, v135, v134, s72
	ml_byte_permute_b32 v16, v133, v132, s72
	ml_byte_permute_b32 v15, v131, v126, s72
	ml_byte_permute_b32 v14, v117, v94, s72
	ml_slb_store_b32x4  v[14:17], v0, s0, #0, null
	sl_add_i32 s1, s0, 0x1000
	ml_byte_permute_b32 v17, v128, v124, s72
	ml_byte_permute_b32 v16, v122, v119, s72
	ml_byte_permute_b32 v15, v118, v86, s72
	ml_byte_permute_b32 v14, v83, v81, s72
	ml_slb_store_b32x4  v[14:17], v0, s0, #512, null
	ml_byte_permute_b32 v13, v13, v12, s72
	ml_byte_permute_b32 v17, v130, v125, s72
	ml_byte_permute_b32 v16, v123, v121, s72
	ml_byte_permute_b32 v15, v120, v110, s72
	ml_byte_permute_b32 v14, v34, v32, s72
	ml_slb_store_b32x4  v[14:17], v0, s1, #0, null
	ml_byte_permute_b32 v12, v11, v10, s72
	ml_byte_permute_b32 v17, v108, v105, s72
	ml_byte_permute_b32 v16, v84, v79, s72
	ml_byte_permute_b32 v15, v78, v66, s72
	ml_byte_permute_b32 v14, v35, v33, s72
	ml_slb_store_b32x4  v[14:17], v0, s1, #512, null
	sl_add_i32 s1, s0, 0x2000
	ml_byte_permute_b32 v17, v109, v107, s72
	ml_byte_permute_b32 v16, v104, v102, s72
	ml_byte_permute_b32 v15, v82, v68, s72
	ml_byte_permute_b32 v14, v55, v52, s72
	ml_slb_store_b32x4  v[14:17], v0, s1, #0, null
	ml_byte_permute_b32 v11, v8, v101, s72
	ml_byte_permute_b32 v17, v80, v56, s72
	ml_byte_permute_b32 v16, v69, v67, s72
	ml_byte_permute_b32 v15, v54, v53, s72
	ml_byte_permute_b32 v14, v51, v50, s72
	ml_slb_store_b32x4  v[14:17], v0, s1, #512, null
	ml_byte_permute_b32 v10, v59, v57, s72
	sl_add_i32 s0, s0, 0x3000
	ml_byte_permute_b32 v7, v9, v7, s72
	ml_slb_store_b32x4  v[10:13], v0, s0, #0, null
	ml_byte_permute_b32 v6, v6, v5, s72
	ml_byte_permute_b32 v5, v4, v3, s72
	ml_byte_permute_b32 v4, v49, v48, s72
	ml_slb_store_b32x4  v[4:7], v0, s0, #512, null
	sl_wait lmcnt(0)
	sl_barrier 
	ml_shl_b32 v0, v64, 0xc
	ml_and_b32 v0, v0, 0x8000
	ml_anyop3_b32 v18, v2, v1, v0, 0xfffffffe
	ml_slb_load_b32x2  v[12:13], v18, s3, #8, null
	sl_add_i32 s0, s3, 0x4000
	.loc	1 40 10                         ; candidate.py:40:10
	sl_cmp_lt_u32 wcr, s43, 0x10
	.loc	1 25 7                          ; candidate.py:25:7
	ml_slb_load_b32x2  v[28:29], v18, s3, #0, null
	ml_slb_load_b32x2  v[14:15], v18, s0, #8, null
	ml_slb_load_b32x2  v[30:31], v18, s0, #0, null
	sl_add_i32 s0, s3, 0x400
	ml_slb_load_b32x2  v[8:9], v18, s0, #8, null
	ml_slb_load_b32x2  v[24:25], v18, s0, #0, null
	sl_add_i32 s0, s3, 0x4400
	ml_slb_load_b32x2  v[10:11], v18, s0, #8, null
	ml_slb_load_b32x2  v[26:27], v18, s0, #0, null
	sl_add_i32 s0, s3, 0x800
	ml_slb_load_b32x2  v[4:5], v18, s0, #8, null
	ml_slb_load_b32x2  v[20:21], v18, s0, #0, null
	sl_add_i32 s0, s3, 0x4800
	ml_slb_load_b32x2  v[6:7], v18, s0, #8, null
	ml_slb_load_b32x2  v[22:23], v18, s0, #0, null
	sl_add_i32 s0, s3, 0xc00
	ml_slb_load_b32x2  v[0:1], v18, s0, #8, null
	ml_slb_load_b32x2  v[16:17], v18, s0, #0, null
	sl_add_i32 s0, s3, 0x4c00
	ml_slb_load_b32x2  v[2:3], v18, s0, #8, null
	ml_slb_load_b32x2  v[18:19], v18, s0, #0, null
	.loc	1 40 7                          ; candidate.py:40:7
	sl_cbr_wcrz BB0_7, wcr
; %bb.6:
	.loc	1 41 78                         ; candidate.py:41:78
	sl_cmp_lt_i32 wcr, s94, 0x7ee
	sl_sub_bi_u64 s[70:71], s[8:9], s[8:9], wcr
	ml_mov_v2s_b32 s12, v242, 0x2d
	ml_mov_v2s_b32 s13, v242, 0x2c
	ml_mov_v2s_b32 s10, v242, 0x2b
	ml_mov_v2s_b32 s11, v242, 0x2a
	sl_cmp_lt_i32 wcr, s12, 0x7ee
	sl_sub_bi_u64 s[68:69], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s13, 0x7ee
	sl_sub_bi_u64 s[66:67], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s10, 0x7ee
	sl_sub_bi_u64 s[64:65], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s11, 0x7ee
	sl_sub_bi_u64 s[62:63], s[8:9], s[8:9], wcr
	ml_mov_v2s_b32 s6, v242, 0x29
	ml_mov_v2s_b32 s7, v242, 0x28
	ml_mov_v2s_b32 s74, v242, 0x27
	ml_mov_v2s_b32 s73, v242, 0x26
	sl_cmp_lt_i32 wcr, s6, 0x7ee
	sl_sub_bi_u64 s[60:61], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s7, 0x7ee
	sl_sub_bi_u64 s[58:59], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s74, 0x7ee
	sl_sub_bi_u64 s[56:57], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s73, 0x7ee
	sl_sub_bi_u64 s[54:55], s[8:9], s[8:9], wcr
	ml_mov_v2s_b32 s5, v242, 0x25
	ml_mov_v2s_b32 s4, v242, 0x24
	ml_mov_v2s_b32 s93, v242, 0x23
	ml_mov_v2s_b32 s92, v242, 0x22
	sl_cmp_lt_i32 wcr, s5, 0x7ee
	sl_sub_bi_u64 s[50:51], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s4, 0x7ee
	sl_sub_bi_u64 s[52:53], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s93, 0x7ee
	sl_sub_bi_u64 s[48:49], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s92, 0x7ee
	sl_sub_bi_u64 s[46:47], s[8:9], s[8:9], wcr
	ml_mov_v2s_b32 s91, v242, 0x21
	ml_mov_v2s_b32 s90, v242, 0x20
	ml_mov_v2s_b32 s89, v242, 0x1f
	ml_mov_v2s_b32 s88, v242, 0x1e
	sl_cmp_lt_i32 wcr, s91, 0x7ee
	sl_sub_bi_u64 s[42:43], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s90, 0x7ee
	sl_sub_bi_u64 s[44:45], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s89, 0x7ee
	sl_sub_bi_u64 s[40:41], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s88, 0x7ee
	sl_sub_bi_u64 s[38:39], s[8:9], s[8:9], wcr
	ml_mov_v2s_b32 s87, v242, 0x1d
	ml_mov_v2s_b32 s86, v242, 0x1c
	ml_mov_v2s_b32 s85, v242, 0x1b
	ml_mov_v2s_b32 s84, v242, 0x1a
	sl_cmp_lt_i32 wcr, s87, 0x7ee
	sl_sub_bi_u64 s[36:37], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s86, 0x7ee
	sl_sub_bi_u64 s[34:35], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s85, 0x7ee
	sl_sub_bi_u64 s[32:33], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s84, 0x7ee
	sl_sub_bi_u64 s[0:1], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v243, s0, 0xa
	ml_mov_s2v_b32 v243, s1, 0xb
	ml_mov_v2s_b32 s83, v242, 0x19
	ml_mov_v2s_b32 s82, v242, 0x18
	ml_mov_v2s_b32 s81, v242, 0x17
	.loc	1 41 37 is_stmt 0               ; candidate.py:41:37
	ml_shl_b32 v32, v36, 0x1
	.loc	1 41 78                         ; candidate.py:41:78
	sl_cmp_lt_i32 wcr, s83, 0x7ee
	sl_sub_bi_u64 s[0:1], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v243, s0, 0x6
	ml_mov_s2v_b32 v243, s1, 0x7
	sl_cmp_lt_i32 wcr, s82, 0x7ee
	sl_sub_bi_u64 s[0:1], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v243, s0, 0x2
	ml_mov_s2v_b32 v243, s1, 0x3
	sl_cmp_lt_i32 wcr, s81, 0x7ee
	sl_sub_bi_u64 s[0:1], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v242, s0, 0x3e
	ml_mov_s2v_b32 v242, s1, 0x3f
	ml_mov_v2s_b32 s80, v242, 0x16
	sl_cmp_lt_i32 wcr, s80, 0x7ee
	sl_sub_bi_u64 s[0:1], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v242, s0, 0x3a
	ml_mov_s2v_b32 v242, s1, 0x3b
	ml_mov_v2s_b32 s79, v242, 0x15
	sl_cmp_lt_i32 wcr, s79, 0x7ee
	sl_sub_bi_u64 s[0:1], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v242, s0, 0x32
	ml_mov_s2v_b32 v242, s1, 0x33
	ml_mov_v2s_b32 s78, v242, 0x14
	sl_cmp_lt_i32 wcr, s78, 0x7ee
	sl_sub_bi_u64 s[0:1], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v242, s0, 0x36
	ml_mov_s2v_b32 v242, s1, 0x37
	ml_mov_v2s_b32 s77, v242, 0x13
	sl_cmp_lt_i32 wcr, s77, 0x7ee
	sl_sub_bi_u64 s[0:1], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v242, s0, 0x2e
	ml_mov_s2v_b32 v242, s1, 0x2f
	ml_mov_v2s_b32 s76, v242, 0x12
	sl_cmp_lt_i32 wcr, s76, 0x7ee
	sl_sub_bi_u64 s[0:1], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v242, s0, 0x30
	ml_mov_s2v_b32 v242, s1, 0x31
	ml_mov_v2s_b32 s75, v242, 0x11
	ml_mov_v2s_b32 s15, v242, 0x10
	.loc	1 41 19                         ; candidate.py:41:19
	ml_mov_v2s_b32 s16, v242, 0x0
	ml_mov_v2s_b32 s17, v242, 0x1
	.loc	1 41 78                         ; candidate.py:41:78
	sl_cmp_lt_i32 wcr, s75, 0x7ee
	sl_sub_bi_u64 s[0:1], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v243, s0, 0x14
	ml_mov_s2v_b32 v243, s1, 0x15
	sl_cmp_lt_i32 wcr, s15, 0x7ee
	sl_sub_bi_u64 s[0:1], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v243, s0, 0x16
	ml_mov_s2v_b32 v243, s1, 0x17
	sl_cmp_lt_i32 wcr, tcr_hi, 0x7ee
	sl_sub_bi_u64 s[0:1], s[8:9], s[8:9], wcr
	.loc	1 41 32                         ; candidate.py:41:32
	ml_mov_s2v_b32 v243, s0, 0x12
	ml_mov_s2v_b32 v243, s1, 0x13
	sl_mull_u32 s0, s94, 0x800
	.loc	1 41 19                         ; candidate.py:41:19
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[2:3], wcr}, s[0:1], 0x1
	ml_mov_v2s_b32 s18, v242, 0x2
	ml_mov_v2s_b32 s19, v242, 0x3
	ml_mov_v2s_b32 s20, v242, 0x4
	ml_mov_v2s_b32 s21, v242, 0x5
	ml_mov_v2s_b32 s22, v242, 0x6
	ml_mov_v2s_b32 s23, v242, 0x7
	ml_mov_v2s_b32 s24, v242, 0x8
	ml_mov_v2s_b32 s25, v242, 0x9
	ml_mov_v2s_b32 s26, v242, 0xa
	ml_mov_v2s_b32 s27, v242, 0xb
	ml_mov_v2s_b32 s28, v242, 0xc
	ml_mov_v2s_b32 s29, v242, 0xd
	ml_mov_v2s_b32 s30, v242, 0xe
	ml_mov_v2s_b32 s31, v242, 0xf
	sl_mov_b32 s94, tcr_hi
	.loc	1 41 37                         ; candidate.py:41:37
	ml_add_i32 v34, s0, v36
	.loc	1 41 19                         ; candidate.py:41:19
	sl_add_i64 s[2:3], s[24:25], s[2:3]
	.loc	1 41 37                         ; candidate.py:41:37
	ml_addo_u32 {v33, tcr}, s2, v32
	ml_mov_b32 v35, s3
	.loc	1 41 50                         ; candidate.py:41:50
	ml_mov_v2s_b32 s0, v33, 0x0
	sl_mov_b32 s3, 0xffffffff
	.loc	1 41 37                         ; candidate.py:41:37
	ml_addc_i32 v35, 0, v35, tcr
	.loc	1 41 50                         ; candidate.py:41:50
	ml_mov_v2s_b32 s1, v35, 0x0
	sl_wait lmcnt(12)
	ml_byte_permute_b32 v35, v30, v28, s72
	ml_mov_b32 v36, s0
	ml_sub_i32 v33, v33, v36
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[70:71], tmsk
	ml_lsa_store_dword v35, s[0:3], signed v33, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s2, s12, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_shl_b32 v34, v34, 0x1
	ml_or_b32 v35, s2, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_sub_i32 v35, v35, v34
	ml_mov_v2s_b32 s28, v35, 0x0
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s2, s13, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v35, s2, v32
	.loc	1 41 50                         ; candidate.py:41:50
	sl_mov_b32 s2, 0x3020706
	ml_add_i32 v36, s28, v33
	ml_sub_i32 v35, v35, v34
	ml_mov_v2s_b32 s28, v35, 0x0
	ml_byte_permute_b32 v28, v30, v28, s2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[68:69], tmsk
	ml_lsa_store_dword v28, s[0:3], signed v36, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s10, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v28, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v30, s28, v33
	ml_sub_i32 v28, v28, v34
	ml_mov_v2s_b32 s28, v28, 0x0
	sl_wait lmcnt(8)
	ml_byte_permute_b32 v28, v26, v24, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[66:67], tmsk
	ml_lsa_store_dword v28, s[0:3], signed v30, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s11, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v28, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v30, s28, v33
	ml_sub_i32 v28, v28, v34
	ml_mov_v2s_b32 s28, v28, 0x0
	ml_byte_permute_b32 v24, v26, v24, s2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[64:65], tmsk
	ml_lsa_store_dword v24, s[0:3], signed v30, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s6, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v24, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v26, s28, v33
	ml_sub_i32 v24, v24, v34
	ml_mov_v2s_b32 s28, v24, 0x0
	sl_wait lmcnt(4)
	ml_byte_permute_b32 v24, v22, v20, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[62:63], tmsk
	ml_lsa_store_dword v24, s[0:3], signed v26, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s7, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v24, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v26, s28, v33
	ml_sub_i32 v24, v24, v34
	ml_mov_v2s_b32 s28, v24, 0x0
	ml_byte_permute_b32 v20, v22, v20, s2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[60:61], tmsk
	ml_lsa_store_dword v20, s[0:3], signed v26, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s74, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v20, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v22, s28, v33
	ml_sub_i32 v20, v20, v34
	ml_mov_v2s_b32 s28, v20, 0x0
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v20, v18, v16, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[58:59], tmsk
	ml_lsa_store_dword v20, s[0:3], signed v22, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s73, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v20, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v22, s28, v33
	ml_sub_i32 v20, v20, v34
	ml_mov_v2s_b32 s28, v20, 0x0
	ml_byte_permute_b32 v16, v18, v16, s2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[56:57], tmsk
	ml_lsa_store_dword v16, s[0:3], signed v22, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s5, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v16, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v18, s28, v33
	ml_sub_i32 v16, v16, v34
	ml_mov_v2s_b32 s28, v16, 0x0
	ml_byte_permute_b32 v16, v31, v29, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[54:55], tmsk
	ml_lsa_store_dword v16, s[0:3], signed v18, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s4, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v16, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v18, s28, v33
	ml_sub_i32 v16, v16, v34
	ml_mov_v2s_b32 s28, v16, 0x0
	ml_byte_permute_b32 v16, v31, v29, s2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[50:51], tmsk
	ml_lsa_store_dword v16, s[0:3], signed v18, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	ml_add_i32 v16, s28, v33
	ml_byte_permute_b32 v18, v27, v25, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[52:53], tmsk
	ml_lsa_store_dword v18, s[0:3], signed v16, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s28, s93, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v16, s28, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_sub_i32 v16, v16, v34
	ml_mov_v2s_b32 s28, v16, 0x0
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s92, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v16, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_byte_permute_b32 v18, v27, v25, s2
	ml_add_i32 v20, s28, v33
	ml_sub_i32 v16, v16, v34
	ml_mov_v2s_b32 s28, v16, 0x0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[48:49], tmsk
	ml_lsa_store_dword v18, s[0:3], signed v20, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s91, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v16, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v18, s28, v33
	ml_sub_i32 v16, v16, v34
	ml_mov_v2s_b32 s28, v16, 0x0
	ml_byte_permute_b32 v16, v23, v21, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[46:47], tmsk
	ml_lsa_store_dword v16, s[0:3], signed v18, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s90, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v16, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v18, s28, v33
	ml_sub_i32 v16, v16, v34
	ml_mov_v2s_b32 s28, v16, 0x0
	ml_byte_permute_b32 v16, v23, v21, s2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[42:43], tmsk
	ml_lsa_store_dword v16, s[0:3], signed v18, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	ml_add_i32 v16, s28, v33
	ml_byte_permute_b32 v18, v19, v17, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[44:45], tmsk
	ml_lsa_store_dword v18, s[0:3], signed v16, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s28, s89, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v16, s28, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_sub_i32 v16, v16, v34
	ml_mov_v2s_b32 s28, v16, 0x0
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s88, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v16, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_byte_permute_b32 v17, v19, v17, s2
	ml_add_i32 v18, s28, v33
	ml_sub_i32 v16, v16, v34
	ml_mov_v2s_b32 s28, v16, 0x0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[40:41], tmsk
	ml_lsa_store_dword v17, s[0:3], signed v18, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s87, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v16, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v17, s28, v33
	ml_sub_i32 v16, v16, v34
	ml_mov_v2s_b32 s28, v16, 0x0
	ml_byte_permute_b32 v16, v14, v12, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[38:39], tmsk
	ml_lsa_store_dword v16, s[0:3], signed v17, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s86, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v16, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v17, s28, v33
	ml_sub_i32 v16, v16, v34
	ml_mov_v2s_b32 s28, v16, 0x0
	ml_byte_permute_b32 v12, v14, v12, s2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[36:37], tmsk
	ml_lsa_store_dword v12, s[0:3], signed v17, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s85, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v12, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v14, s28, v33
	ml_sub_i32 v12, v12, v34
	ml_mov_v2s_b32 s28, v12, 0x0
	ml_byte_permute_b32 v12, v10, v8, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[34:35], tmsk
	ml_lsa_store_dword v12, s[0:3], signed v14, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s84, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v12, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v14, s28, v33
	ml_sub_i32 v12, v12, v34
	ml_mov_v2s_b32 s28, v12, 0x0
	ml_byte_permute_b32 v8, v10, v8, s2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[32:33], tmsk
	ml_lsa_store_dword v8, s[0:3], signed v14, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s83, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v8, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v10, s28, v33
	ml_sub_i32 v8, v8, v34
	ml_mov_v2s_b32 s28, v8, 0x0
	ml_byte_permute_b32 v8, v6, v4, s72
	ml_mov_v2s_b32 s4, v243, 0xa
	ml_mov_v2s_b32 s5, v243, 0xb
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v8, s[0:3], signed v10, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s29, s82, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v8, s29, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v10, s28, v33
	ml_sub_i32 v8, v8, v34
	ml_mov_v2s_b32 s28, v8, 0x0
	ml_byte_permute_b32 v4, v6, v4, s2
	ml_mov_v2s_b32 s4, v243, 0x6
	ml_mov_v2s_b32 s5, v243, 0x7
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v4, s[0:3], signed v10, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s26, s81, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v4, s26, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v6, s28, v33
	ml_sub_i32 v4, v4, v34
	ml_mov_v2s_b32 s26, v4, 0x0
	ml_byte_permute_b32 v4, v2, v0, s72
	ml_mov_v2s_b32 s4, v243, 0x2
	ml_mov_v2s_b32 s5, v243, 0x3
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v4, s[0:3], signed v6, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s24, s80, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v4, s24, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v6, s26, v33
	ml_sub_i32 v4, v4, v34
	ml_mov_v2s_b32 s24, v4, 0x0
	ml_byte_permute_b32 v0, v2, v0, s2
	ml_mov_v2s_b32 s4, v242, 0x3e
	ml_mov_v2s_b32 s5, v242, 0x3f
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v0, s[0:3], signed v6, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s22, s79, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v0, s22, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v2, s24, v33
	ml_sub_i32 v0, v0, v34
	ml_mov_v2s_b32 s22, v0, 0x0
	ml_byte_permute_b32 v0, v15, v13, s72
	ml_mov_v2s_b32 s4, v242, 0x3a
	ml_mov_v2s_b32 s5, v242, 0x3b
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v0, s[0:3], signed v2, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s20, s78, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v0, s20, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v2, s22, v33
	ml_sub_i32 v0, v0, v34
	ml_mov_v2s_b32 s20, v0, 0x0
	ml_byte_permute_b32 v0, v15, v13, s2
	ml_mov_v2s_b32 s4, v242, 0x32
	ml_mov_v2s_b32 s5, v242, 0x33
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v0, s[0:3], signed v2, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	ml_add_i32 v0, s20, v33
	ml_byte_permute_b32 v2, v11, v9, s72
	ml_mov_v2s_b32 s4, v242, 0x36
	ml_mov_v2s_b32 s5, v242, 0x37
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v2, s[0:3], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s16, s77, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v0, s16, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_sub_i32 v0, v0, v34
	ml_mov_v2s_b32 s16, v0, 0x0
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s17, s76, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v0, s17, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_byte_permute_b32 v2, v11, v9, s2
	ml_add_i32 v4, s16, v33
	ml_sub_i32 v0, v0, v34
	ml_mov_v2s_b32 s16, v0, 0x0
	ml_mov_v2s_b32 s4, v242, 0x2e
	ml_mov_v2s_b32 s5, v242, 0x2f
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v2, s[0:3], signed v4, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s14, s75, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v0, s14, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_add_i32 v2, s16, v33
	ml_sub_i32 v0, v0, v34
	ml_mov_v2s_b32 s14, v0, 0x0
	ml_byte_permute_b32 v0, v7, v5, s72
	ml_mov_v2s_b32 s4, v242, 0x30
	ml_mov_v2s_b32 s5, v242, 0x31
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v0, s[0:3], signed v2, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	ml_add_i32 v0, s14, v33
	ml_byte_permute_b32 v2, v7, v5, s2
	ml_mov_v2s_b32 s4, v243, 0x14
	ml_mov_v2s_b32 s5, v243, 0x15
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v2, s[0:3], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 41 19                         ; candidate.py:41:19
	sl_mull_u32 s10, s15, 0x1000
	sl_mull_u32 s11, s94, 0x1000
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v0, s10, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_sub_i32 v0, v0, v34
	ml_mov_v2s_b32 s10, v0, 0x0
	.loc	1 41 37                         ; candidate.py:41:37
	ml_or_b32 v0, s11, v32
	.loc	1 41 50                         ; candidate.py:41:50
	ml_byte_permute_b32 v2, v3, v1, s72
	ml_sub_i32 v0, v0, v34
	ml_add_i32 v4, s10, v33
	ml_mov_v2s_b32 s10, v0, 0x0
	ml_mov_v2s_b32 s4, v243, 0x16
	ml_mov_v2s_b32 s5, v243, 0x17
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v2, s[0:3], signed v4, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	ml_byte_permute_b32 v0, v3, v1, s2
	ml_add_i32 v1, s10, v33
	ml_mov_v2s_b32 s4, v243, 0x12
	ml_mov_v2s_b32 s5, v243, 0x13
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v0, s[0:3], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 40 7 is_stmt 1                ; candidate.py:40:7
	sl_jump BB0_8
BB0_7:
	.loc	1 0 0 is_stmt 0                 ; candidate.py:0
	sl_or_b32 {s2, wcr}, s2, 0x0
	sl_mov_b32 s0, 0xfffff800
	sl_mov_b32 s1, 0x100
	sl_csel_b32 s0, s0, 0xfffff700, wcr
	sl_csel_b32 s73, s1, 0xa00, wcr
	.loc	1 42 9 is_stmt 1                ; candidate.py:42:9
	ml_mov_v2s_b32 s12, v242, 0x0
	ml_mov_v2s_b32 s13, v242, 0x1
	ml_mov_v2s_b32 s14, v242, 0x2
	ml_mov_v2s_b32 s15, v242, 0x3
	ml_mov_v2s_b32 s16, v242, 0x4
	ml_mov_v2s_b32 s17, v242, 0x5
	ml_mov_v2s_b32 s18, v242, 0x6
	ml_mov_v2s_b32 s19, v242, 0x7
	ml_mov_v2s_b32 s20, v242, 0x8
	ml_mov_v2s_b32 s21, v242, 0x9
	ml_mov_v2s_b32 s22, v242, 0xa
	ml_mov_v2s_b32 s23, v242, 0xb
	ml_mov_v2s_b32 s24, v242, 0xc
	ml_mov_v2s_b32 s25, v242, 0xd
	ml_mov_v2s_b32 s26, v242, 0xe
	ml_mov_v2s_b32 s27, v242, 0xf
	ml_mov_v2s_b32 s16, v242, 0x2d
	ml_mov_v2s_b32 s15, v242, 0x2c
	sl_csel_b64 s[70:71], s[22:23], s[24:25], wcr
	.loc	1 43 87                         ; candidate.py:43:87
	sl_cmp_lt_i32 wcr, s94, 0x7ee
	sl_sub_bi_u64 s[68:69], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s16, 0x7ee
	sl_sub_bi_u64 s[66:67], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s15, 0x7ee
	sl_sub_bi_u64 s[64:65], s[8:9], s[8:9], wcr
	ml_mov_v2s_b32 s14, v242, 0x2b
	ml_mov_v2s_b32 s13, v242, 0x2a
	ml_mov_v2s_b32 s12, v242, 0x29
	ml_mov_v2s_b32 s10, v242, 0x28
	sl_cmp_lt_i32 wcr, s14, 0x7ee
	sl_sub_bi_u64 s[62:63], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s13, 0x7ee
	sl_sub_bi_u64 s[60:61], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s12, 0x7ee
	sl_sub_bi_u64 s[58:59], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s10, 0x7ee
	sl_sub_bi_u64 s[56:57], s[8:9], s[8:9], wcr
	ml_mov_v2s_b32 s11, v242, 0x27
	ml_mov_v2s_b32 s6, v242, 0x26
	ml_mov_v2s_b32 s7, v242, 0x25
	ml_mov_v2s_b32 s76, v242, 0x24
	sl_cmp_lt_i32 wcr, s11, 0x7ee
	sl_sub_bi_u64 s[54:55], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s6, 0x7ee
	sl_sub_bi_u64 s[52:53], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s7, 0x7ee
	sl_sub_bi_u64 s[50:51], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s76, 0x7ee
	sl_sub_bi_u64 s[48:49], s[8:9], s[8:9], wcr
	ml_mov_v2s_b32 s5, v242, 0x23
	ml_mov_v2s_b32 s4, v242, 0x22
	ml_mov_v2s_b32 s93, v242, 0x21
	ml_mov_v2s_b32 s92, v242, 0x20
	sl_cmp_lt_i32 wcr, s5, 0x7ee
	sl_sub_bi_u64 s[46:47], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s4, 0x7ee
	sl_sub_bi_u64 s[44:45], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s93, 0x7ee
	sl_sub_bi_u64 s[42:43], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s92, 0x7ee
	sl_sub_bi_u64 s[40:41], s[8:9], s[8:9], wcr
	ml_mov_v2s_b32 s91, v242, 0x1f
	ml_mov_v2s_b32 s90, v242, 0x1e
	ml_mov_v2s_b32 s89, v242, 0x1d
	ml_mov_v2s_b32 s88, v242, 0x1c
	sl_cmp_lt_i32 wcr, s91, 0x7ee
	sl_sub_bi_u64 s[38:39], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s90, 0x7ee
	sl_sub_bi_u64 s[36:37], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s89, 0x7ee
	sl_sub_bi_u64 s[34:35], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s88, 0x7ee
	sl_sub_bi_u64 s[32:33], s[8:9], s[8:9], wcr
	ml_mov_v2s_b32 s87, v242, 0x1b
	ml_mov_v2s_b32 s86, v242, 0x1a
	ml_mov_v2s_b32 s85, v242, 0x19
	ml_mov_v2s_b32 s84, v242, 0x18
	sl_cmp_lt_i32 wcr, s87, 0x7ee
	sl_sub_bi_u64 s[30:31], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s86, 0x7ee
	sl_sub_bi_u64 s[28:29], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s85, 0x7ee
	sl_sub_bi_u64 s[26:27], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s84, 0x7ee
	sl_sub_bi_u64 s[24:25], s[8:9], s[8:9], wcr
	ml_mov_v2s_b32 s83, v242, 0x17
	ml_mov_v2s_b32 s82, v242, 0x16
	ml_mov_v2s_b32 s81, v242, 0x15
	ml_mov_v2s_b32 s80, v242, 0x14
	sl_cmp_lt_i32 wcr, s83, 0x7ee
	sl_sub_bi_u64 s[22:23], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s82, 0x7ee
	sl_sub_bi_u64 s[20:21], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s81, 0x7ee
	sl_sub_bi_u64 s[18:19], s[8:9], s[8:9], wcr
	sl_cmp_lt_i32 wcr, s80, 0x7ee
	sl_sub_bi_u64 s[2:3], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v242, s2, 0x2e
	ml_mov_s2v_b32 v242, s3, 0x2f
	ml_mov_v2s_b32 s79, v242, 0x13
	ml_mov_v2s_b32 s78, v242, 0x12
	.loc	1 43 39 is_stmt 0               ; candidate.py:43:39
	ml_shl_b32 v32, v36, 0x1
	.loc	1 43 87                         ; candidate.py:43:87
	sl_cmp_lt_i32 wcr, s79, 0x7ee
	sl_sub_bi_u64 s[2:3], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v243, s2, 0x14
	ml_mov_s2v_b32 v243, s3, 0x15
	sl_cmp_lt_i32 wcr, s78, 0x7ee
	sl_sub_bi_u64 s[2:3], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v242, s2, 0x30
	ml_mov_s2v_b32 v242, s3, 0x31
	ml_mov_v2s_b32 s77, v242, 0x11
	ml_mov_v2s_b32 s17, v242, 0x10
	sl_cmp_lt_i32 wcr, s77, 0x7ee
	sl_sub_bi_u64 s[2:3], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v243, s2, 0x12
	ml_mov_s2v_b32 v243, s3, 0x13
	sl_cmp_lt_i32 wcr, s17, 0x7ee
	sl_sub_bi_u64 s[2:3], s[8:9], s[8:9], wcr
	ml_mov_s2v_b32 v243, s2, 0x16
	ml_mov_s2v_b32 v243, s3, 0x17
	sl_cmp_lt_i32 wcr, tcr_hi, 0x7ee
	sl_sub_bi_u64 s[2:3], s[8:9], s[8:9], wcr
	.loc	1 43 35                         ; candidate.py:43:35
	ml_mov_s2v_b32 v242, s2, 0x0
	ml_mov_s2v_b32 v242, s3, 0x1
	sl_mull_u32 s2, s73, s94
	.loc	1 43 22                         ; candidate.py:43:22
	sl_sra_b32 {s3, wcr}, s2, 0x1f
	sl_shl_b64 {s[74:75], wcr}, s[2:3], 0x1
	sl_add_i64 s[70:71], s[70:71], s[74:75]
	.loc	1 43 39                         ; candidate.py:43:39
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[0:1], s[70:71], s[0:1]
	sl_mov_b32 s70, tcr_hi
	ml_addo_u32 {v32, tcr}, s0, v32
	ml_mov_b32 v33, s1
	.loc	1 43 59                         ; candidate.py:43:59
	ml_mov_v2s_b32 s0, v32, 0x0
	sl_mov_b32 s3, 0xffffffff
	.loc	1 43 39                         ; candidate.py:43:39
	ml_addc_i32 v33, 0, v33, tcr
	.loc	1 43 59                         ; candidate.py:43:59
	ml_mov_v2s_b32 s1, v33, 0x0
	sl_wait lmcnt(12)
	ml_byte_permute_b32 v33, v30, v28, s72
	ml_mov_b32 v34, s0
	ml_sub_i32 v32, v32, v34
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[68:69], tmsk
	ml_lsa_store_dword v33, s[0:3], signed v32, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s68, s73, s16
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s68, s68, s2
	sl_mull_u32 s68, s68, 0x2
	ml_add_i32 v33, s68, v32
	sl_mov_b32 s68, 0x3020706
	ml_byte_permute_b32 v28, v30, v28, s68
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[66:67], tmsk
	ml_lsa_store_dword v28, s[0:3], signed v33, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s66, s73, s15
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s66, s66, s2
	sl_mull_u32 s66, s66, 0x2
	ml_add_i32 v28, s66, v32
	sl_wait lmcnt(8)
	ml_byte_permute_b32 v30, v26, v24, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[64:65], tmsk
	ml_lsa_store_dword v30, s[0:3], signed v28, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s64, s73, s14
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s64, s64, s2
	sl_mull_u32 s64, s64, 0x2
	ml_add_i32 v28, s64, v32
	ml_byte_permute_b32 v24, v26, v24, s68
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[62:63], tmsk
	ml_lsa_store_dword v24, s[0:3], signed v28, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s62, s73, s13
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s62, s62, s2
	sl_mull_u32 s62, s62, 0x2
	ml_add_i32 v24, s62, v32
	sl_wait lmcnt(4)
	ml_byte_permute_b32 v26, v22, v20, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[60:61], tmsk
	ml_lsa_store_dword v26, s[0:3], signed v24, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s60, s73, s12
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s60, s60, s2
	sl_mull_u32 s60, s60, 0x2
	ml_add_i32 v24, s60, v32
	ml_byte_permute_b32 v20, v22, v20, s68
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[58:59], tmsk
	ml_lsa_store_dword v20, s[0:3], signed v24, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s58, s73, s10
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s58, s58, s2
	sl_mull_u32 s58, s58, 0x2
	ml_add_i32 v20, s58, v32
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v22, v18, v16, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[56:57], tmsk
	ml_lsa_store_dword v22, s[0:3], signed v20, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s56, s73, s11
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s56, s56, s2
	sl_mull_u32 s56, s56, 0x2
	ml_add_i32 v20, s56, v32
	ml_byte_permute_b32 v16, v18, v16, s68
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[54:55], tmsk
	ml_lsa_store_dword v16, s[0:3], signed v20, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s54, s73, s6
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s54, s54, s2
	sl_mull_u32 s54, s54, 0x2
	ml_add_i32 v16, s54, v32
	ml_byte_permute_b32 v18, v31, v29, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[52:53], tmsk
	ml_lsa_store_dword v18, s[0:3], signed v16, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s52, s73, s7
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s52, s52, s2
	sl_mull_u32 s52, s52, 0x2
	ml_add_i32 v16, s52, v32
	ml_byte_permute_b32 v18, v31, v29, s68
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[50:51], tmsk
	ml_lsa_store_dword v18, s[0:3], signed v16, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s50, s73, s76
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s50, s50, s2
	sl_mull_u32 s50, s50, 0x2
	ml_add_i32 v16, s50, v32
	ml_byte_permute_b32 v18, v27, v25, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[48:49], tmsk
	ml_lsa_store_dword v18, s[0:3], signed v16, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s48, s73, s5
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s48, s48, s2
	sl_mull_u32 s48, s48, 0x2
	ml_add_i32 v16, s48, v32
	ml_byte_permute_b32 v18, v27, v25, s68
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[46:47], tmsk
	ml_lsa_store_dword v18, s[0:3], signed v16, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s46, s73, s4
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s46, s46, s2
	sl_mull_u32 s46, s46, 0x2
	ml_add_i32 v16, s46, v32
	ml_byte_permute_b32 v18, v23, v21, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[44:45], tmsk
	ml_lsa_store_dword v18, s[0:3], signed v16, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s44, s73, s93
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s44, s44, s2
	sl_mull_u32 s44, s44, 0x2
	ml_add_i32 v16, s44, v32
	ml_byte_permute_b32 v18, v23, v21, s68
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[42:43], tmsk
	ml_lsa_store_dword v18, s[0:3], signed v16, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s42, s73, s92
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s42, s42, s2
	sl_mull_u32 s42, s42, 0x2
	ml_add_i32 v16, s42, v32
	ml_byte_permute_b32 v18, v19, v17, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[40:41], tmsk
	ml_lsa_store_dword v18, s[0:3], signed v16, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s40, s73, s91
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s40, s40, s2
	sl_mull_u32 s40, s40, 0x2
	ml_add_i32 v16, s40, v32
	ml_byte_permute_b32 v17, v19, v17, s68
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[38:39], tmsk
	ml_lsa_store_dword v17, s[0:3], signed v16, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s38, s73, s90
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s38, s38, s2
	sl_mull_u32 s38, s38, 0x2
	ml_add_i32 v16, s38, v32
	ml_byte_permute_b32 v17, v14, v12, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[36:37], tmsk
	ml_lsa_store_dword v17, s[0:3], signed v16, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s36, s73, s89
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s36, s36, s2
	sl_mull_u32 s36, s36, 0x2
	ml_add_i32 v16, s36, v32
	ml_byte_permute_b32 v12, v14, v12, s68
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[34:35], tmsk
	ml_lsa_store_dword v12, s[0:3], signed v16, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s34, s73, s88
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s34, s34, s2
	sl_mull_u32 s34, s34, 0x2
	ml_add_i32 v12, s34, v32
	ml_byte_permute_b32 v14, v10, v8, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[32:33], tmsk
	ml_lsa_store_dword v14, s[0:3], signed v12, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s32, s73, s87
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s32, s32, s2
	sl_mull_u32 s32, s32, 0x2
	ml_add_i32 v12, s32, v32
	ml_byte_permute_b32 v8, v10, v8, s68
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[30:31], tmsk
	ml_lsa_store_dword v8, s[0:3], signed v12, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s30, s73, s86
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s30, s30, s2
	sl_mull_u32 s30, s30, 0x2
	ml_add_i32 v8, s30, v32
	ml_byte_permute_b32 v10, v6, v4, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[28:29], tmsk
	ml_lsa_store_dword v10, s[0:3], signed v8, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s28, s73, s85
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s28, s28, s2
	sl_mull_u32 s28, s28, 0x2
	ml_add_i32 v8, s28, v32
	ml_byte_permute_b32 v4, v6, v4, s68
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[26:27], tmsk
	ml_lsa_store_dword v4, s[0:3], signed v8, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s26, s73, s84
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s26, s26, s2
	sl_mull_u32 s26, s26, 0x2
	ml_add_i32 v4, s26, v32
	ml_byte_permute_b32 v6, v2, v0, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[24:25], tmsk
	ml_lsa_store_dword v6, s[0:3], signed v4, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s24, s73, s83
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s24, s24, s2
	sl_mull_u32 s24, s24, 0x2
	ml_add_i32 v4, s24, v32
	ml_byte_permute_b32 v0, v2, v0, s68
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[22:23], tmsk
	ml_lsa_store_dword v0, s[0:3], signed v4, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s22, s73, s82
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s22, s22, s2
	sl_mull_u32 s22, s22, 0x2
	ml_add_i32 v0, s22, v32
	ml_byte_permute_b32 v2, v15, v13, s72
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[20:21], tmsk
	ml_lsa_store_dword v2, s[0:3], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s20, s73, s81
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s20, s20, s2
	sl_mull_u32 s20, s20, 0x2
	ml_add_i32 v0, s20, v32
	ml_byte_permute_b32 v2, v15, v13, s68
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[18:19], tmsk
	ml_lsa_store_dword v2, s[0:3], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s18, s73, s80
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s18, s18, s2
	sl_mull_u32 s18, s18, 0x2
	ml_add_i32 v0, s18, v32
	ml_byte_permute_b32 v2, v11, v9, s72
	ml_mov_v2s_b32 s4, v242, 0x2e
	ml_mov_v2s_b32 s5, v242, 0x2f
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v2, s[0:3], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s16, s73, s79
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s16, s16, s2
	sl_mull_u32 s16, s16, 0x2
	ml_add_i32 v0, s16, v32
	ml_byte_permute_b32 v2, v11, v9, s68
	ml_mov_v2s_b32 s4, v243, 0x14
	ml_mov_v2s_b32 s5, v243, 0x15
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v2, s[0:3], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s14, s73, s78
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s14, s14, s2
	sl_mull_u32 s14, s14, 0x2
	ml_add_i32 v0, s14, v32
	ml_byte_permute_b32 v2, v7, v5, s72
	ml_mov_v2s_b32 s4, v242, 0x30
	ml_mov_v2s_b32 s5, v242, 0x31
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v2, s[0:3], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s12, s73, s77
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s12, s12, s2
	sl_mull_u32 s12, s12, 0x2
	ml_add_i32 v0, s12, v32
	ml_byte_permute_b32 v2, v7, v5, s68
	ml_mov_v2s_b32 s4, v243, 0x12
	ml_mov_v2s_b32 s5, v243, 0x13
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v2, s[0:3], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	ml_byte_permute_b32 v0, v3, v1, s72
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s10, s73, s17
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s10, s10, s2
	sl_mull_u32 s10, s10, 0x2
	ml_add_i32 v2, s10, v32
	ml_mov_v2s_b32 s4, v243, 0x16
	ml_mov_v2s_b32 s5, v243, 0x17
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v0, s[0:3], signed v2, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 43 35                         ; candidate.py:43:35
	sl_mull_u32 s6, s73, s70
	.loc	1 43 59                         ; candidate.py:43:59
	sl_sub_i32 s2, s6, s2
	ml_byte_permute_b32 v0, v3, v1, s68
	sl_mull_u32 s2, s2, 0x2
	ml_add_i32 v1, s2, v32
	ml_mov_v2s_b32 s4, v242, 0x0
	ml_mov_v2s_b32 s5, v242, 0x1
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v0, s[0:3], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
BB0_8:
	.loc	1 40 4 is_stmt 1                ; candidate.py:40:4
	sl_eop 
.Ltmp1:
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	qkv_rope.kd
	.type	qkv_rope.kd,@object
	.size	qkv_rope.kd, 64
qkv_rope.kd:
	.asciz	"\000\000\000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	qkv_rope@rel64-qkv_rope.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	537404
	.asciz	"\003\000\224\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	qkv_rope, .Lfunc_end0-qkv_rope
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 24904
; NumSgprs: 99
; NumVgprs: 244
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 12
; VGPRBlocks: 60
; NumSGPRsForWarpsPerNU: 95
; NumVGPRsForWarpsPerNR: 244
; ReqNTIDx: 0
; MaxNTIDx: 0
; MinCTASm: 0
; ActiveWarp: 1
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
	.long	157                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0x96 DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"candidate.py"                  ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/workspace/experiments/minicpm-s2/framework/20261026T064944259294Z-biv150-qkv-rope-fusion-component/source" ; DW_AT_comp_dir
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
      - .address_space:  global
        .name:           KArg_6
        .offset:         48
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_7
        .offset:         56
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_8
        .offset:         64
        .size:           8
        .value_kind:     global_buffer
    .group_segment_fixed_size: 0
    .kernarg_segment_align: 8
    .kernarg_segment_size: 72
    .max_flat_workgroup_size: 0
    .name:           qkv_rope
    .private_segment_fixed_size: 0
    .sgpr_count:     99
    .sgpr_spill_count: 165
    .symbol:         qkv_rope.kd
    .vgpr_count:     244
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
