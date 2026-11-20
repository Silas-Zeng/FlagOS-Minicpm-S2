	.text
	.globl	down_group256                   ; -- Begin function down_group256
	.p2align	3
	.type	down_group256,@function
	.iluvatar_kernel down_group256
down_group256:                          ; @down_group256
.Lfunc_begin0:
	.file	1 "/workspace/experiments/minicpm-s2/framework/20261026T062610126686Z-biv150-down-group256-component/source" "candidate.py"
	.loc	1 33 0                          ; candidate.py:33:0
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
		granulated_workitem_vgpr_count = 26
		granulated_warp_sgpr_count = 11
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
		kernarg_segment_byte_size = 56
		workgroup_fbarrier_count = 0
		warp_sgpr_count = 96
		workitem_vgpr_count = 107
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
	sl_mov_b32 s1, tcr_lo
	sl_mov_b32 s38, tcr_lo
	ml_vrf_init_u32 v8, tcr
.Ltmp0:
	.loc	1 36 24 prologue_end            ; candidate.py:36:24
	sl_lsa_load_b32x16 s[20:35], s[4:5], noreg, #0, ca
	.loc	1 37 27                         ; candidate.py:37:27
	sl_and_b32 {s74, wcr}, s6, 0x7fffffe0
	.loc	1 37 45 is_stmt 0               ; candidate.py:37:45
	sl_and_b32 {s0, wcr}, tcr_lo, 0xc0
	sl_bfe2_b32 s2, tcr_lo, 0x46
	.loc	1 37 32                         ; candidate.py:37:32
	sl_add_i32 s2, s2, s74
	sl_add_i32 s7, s2, 0x4
	sl_add_i32 s75, s2, 0x8
	sl_add_i32 s76, s2, 0xc
	sl_add_i32 s77, s2, 0x10
	sl_add_i32 s78, s2, 0x14
	sl_add_i32 s79, s2, 0x18
	sl_add_i32 s80, s2, 0x1c
	.loc	1 39 21 is_stmt 1               ; candidate.py:39:21
	ml_shl_b32 v0, v8, 0x2
	ml_and_b32 v7, v0, 0xfc
	.loc	1 44 38                         ; candidate.py:44:38
	sl_cmp_lt_u32 wcr, s2, 0x7ee
	sl_sub_bi_u32 s18, s8, s8, wcr
	.loc	1 43 37                         ; candidate.py:43:37
	sl_mull_u32 s2, s2, 0x1800
	sl_mull_u32 s4, s7, 0x1800
	sl_mull_u32 s10, s75, 0x1800
	sl_mull_u32 s12, s76, 0x1800
	sl_mull_u32 s14, s77, 0x1800
	sl_mull_u32 s16, s78, 0x1800
	sl_wait smcnt(0)
	sl_mull_u32 s30, s79, 0x1800
	sl_mull_u32 s32, s80, 0x1800
	.loc	1 43 24 is_stmt 0               ; candidate.py:43:24
	sl_sra_b32 {s3, wcr}, s2, 0x1f
	sl_add_i64 s[36:37], s[20:21], s[2:3]
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_add_i64 s[40:41], s[20:21], s[4:5]
	sl_sra_b32 {s11, wcr}, s10, 0x1f
	sl_add_i64 s[44:45], s[20:21], s[10:11]
	sl_sra_b32 {s13, wcr}, s12, 0x1f
	sl_add_i64 s[48:49], s[20:21], s[12:13]
	sl_sra_b32 {s15, wcr}, s14, 0x1f
	sl_add_i64 s[52:53], s[20:21], s[14:15]
	sl_sra_b32 {s17, wcr}, s16, 0x1f
	sl_add_i64 s[56:57], s[20:21], s[16:17]
	sl_sra_b32 {s31, wcr}, s30, 0x1f
	sl_add_i64 s[60:61], s[20:21], s[30:31]
	sl_sra_b32 {s33, wcr}, s32, 0x1f
	sl_add_i64 s[64:65], s[20:21], s[32:33]
	.loc	1 43 41                         ; candidate.py:43:41
	ml_mov_b32 v34, 0x0
	sl_mov_b32 s31, 0x0
	ml_mov_b32 v9, 0x0
	ml_and_b32 v11, v8, 0x3f
	sl_cmp_lt_u32 wcr, s7, 0x7ee
	sl_sub_bi_u32 s19, s8, s8, wcr
	ml_mov_b32 v53, 0x0
	ml_mov_b32 v54, 0x0
	ml_mov_b32 v55, 0x0
	ml_mov_b32 v56, 0x0
	ml_mov_b32 v49, 0x0
	ml_mov_b32 v50, 0x0
	ml_mov_b32 v51, 0x0
	ml_mov_b32 v52, 0x0
	ml_mov_b32 v57, 0x0
	ml_mov_b32 v5, 0x0
	ml_mov_b32 v6, 0x0
	ml_mov_b32 v4, 0x0
	ml_mov_b32 v65, 0x0
	ml_mov_b32 v63, 0x0
	ml_mov_b32 v64, 0x0
	ml_mov_b32 v62, 0x0
	ml_mov_b32 v58, 0x0
	ml_mov_b32 v59, 0x0
	ml_mov_b32 v60, 0x0
	ml_mov_b32 v61, 0x0
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v2, 0x0
	ml_mov_b32 v3, 0x0
	ml_mov_b32 v45, 0x0
	ml_mov_b32 v46, 0x0
	ml_mov_b32 v47, 0x0
	ml_mov_b32 v48, 0x0
	.loc	1 43 20                         ; candidate.py:43:20
	sl_or_b32 {s18, wcr}, s18, 0x0
	ml_mov_b32 v12, 0x0
	sl_cbr_wcrz BB0_15, wcr
; %bb.1:
	sl_mov_b32 s39, 0xfff00004
	ml_lsa_load_dword v10, s[36:39], unsigned v11, noreg, #0, ca|mie
	ml_mov_b32 v13, 0x0
	sl_or_b32 {s19, wcr}, s19, 0x0
	sl_cbr_wcrz BB0_3, wcr
; %bb.2:
	sl_mov_b64 s[42:43], s[38:39]
	ml_lsa_load_dword v12, s[40:43], unsigned v11, noreg, #0, ca|mie
BB0_3:
	.loc	1 44 38 is_stmt 1               ; candidate.py:44:38
	sl_cmp_lt_u32 wcr, s75, 0x7ee
	.loc	1 43 20                         ; candidate.py:43:20
	sl_cbr_wcrz BB0_5, wcr
; %bb.4:
	sl_mov_b32 s47, 0xfff00004
	ml_lsa_load_dword v13, s[44:47], unsigned v11, noreg, #0, ca|mie
BB0_5:
	.loc	1 44 38                         ; candidate.py:44:38
	sl_cmp_lt_u32 wcr, s76, 0x7ee
	.loc	1 43 20                         ; candidate.py:43:20
	sl_cbr_wcrz BB0_7, wcr
; %bb.6:
	sl_mov_b32 s51, 0xfff00004
	ml_lsa_load_dword v3, s[48:51], unsigned v11, noreg, #0, ca|mie
BB0_7:
	.loc	1 44 38                         ; candidate.py:44:38
	sl_cmp_lt_u32 wcr, s77, 0x7ee
	.loc	1 43 20                         ; candidate.py:43:20
	sl_cbr_wcrz BB0_9, wcr
; %bb.8:
	sl_mov_b32 s55, 0xfff00004
	ml_lsa_load_dword v0, s[52:55], unsigned v11, noreg, #0, ca|mie
BB0_9:
	.loc	1 44 38                         ; candidate.py:44:38
	sl_cmp_lt_u32 wcr, s78, 0x7ee
	.loc	1 43 20                         ; candidate.py:43:20
	ml_mov_b32 v14, 0x0
	sl_cbr_wcrz BB0_11, wcr
; %bb.10:
	sl_mov_b32 s59, 0xfff00004
	ml_lsa_load_dword v1, s[56:59], unsigned v11, noreg, #0, ca|mie
BB0_11:
	.loc	1 44 38                         ; candidate.py:44:38
	sl_cmp_lt_u32 wcr, s79, 0x7ee
	.loc	1 43 20                         ; candidate.py:43:20
	sl_cbr_wcrz BB0_13, wcr
; %bb.12:
	sl_mov_b32 s63, 0xfff00004
	ml_lsa_load_dword v14, s[60:63], unsigned v11, noreg, #0, ca|mie
BB0_13:
	sl_wait vmcnt(0)
	ml_and_b32 v45, v1, 0xff
	ml_bfe2_b32 v46, v1, 0x108
	ml_bfe2_b32 v47, v1, 0x110
	ml_bfe2_b32 v48, v1, 0x118
	ml_and_b32 v52, v0, 0xff
	ml_bfe2_b32 v51, v0, 0x108
	ml_bfe2_b32 v50, v0, 0x110
	ml_bfe2_b32 v49, v0, 0x118
	ml_and_b32 v0, v3, 0xff
	ml_bfe2_b32 v1, v3, 0x108
	ml_bfe2_b32 v2, v3, 0x110
	ml_bfe2_b32 v3, v3, 0x118
	ml_and_b32 v4, v13, 0xff
	ml_bfe2_b32 v6, v13, 0x108
	ml_bfe2_b32 v5, v13, 0x110
	ml_bfe2_b32 v57, v13, 0x118
	ml_and_b32 v58, v12, 0xff
	ml_bfe2_b32 v59, v12, 0x108
	ml_bfe2_b32 v60, v12, 0x110
	ml_bfe2_b32 v61, v12, 0x118
	ml_and_b32 v62, v10, 0xff
	ml_bfe2_b32 v64, v10, 0x108
	ml_bfe2_b32 v63, v10, 0x110
	ml_bfe2_b32 v65, v10, 0x118
	ml_and_b32 v56, v14, 0xff
	ml_bfe2_b32 v55, v14, 0x108
	ml_bfe2_b32 v54, v14, 0x110
	ml_bfe2_b32 v53, v14, 0x118
	.loc	1 44 38                         ; candidate.py:44:38
	sl_cmp_lt_u32 wcr, s80, 0x7ee
	.loc	1 43 20                         ; candidate.py:43:20
	ml_mov_b32 v12, 0x0
	sl_cbr_wcrz BB0_15, wcr
; %bb.14:
	sl_mov_b32 s67, 0xfff00004
	ml_lsa_load_dword v12, s[64:67], unsigned v11, noreg, #0, ca|mie
BB0_15:                                 ; %.thread129
	.loc	1 38 26                         ; candidate.py:38:26
	sl_mull_u32 s2, s6, 0x40
	sl_and_b32 {s20, wcr}, s2, 0x7c0
	.loc	1 45 37                         ; candidate.py:45:37
	sl_mull_u32 s30, s20, 0x1800
	.loc	1 45 24 is_stmt 0               ; candidate.py:45:24
	sl_add_i64 s[32:33], s[24:25], s[30:31]
	.loc	1 45 20                         ; candidate.py:45:20
	sl_bfe2_b32 s21, s1, 0x26
	sl_bfe2_b32 s1, s38, 0x27
	sl_mov_b32 s71, 0x1800
	sl_mov_b32 s70, 0xffffffff
	sl_mov_b64 s[34:35], s[70:71]
	sl_mull_u32 s2, s1, 0x1000
	sl_mull_u32 s3, s21, 0x400
	sl_add_i32 s30, s3, s2
	sl_mull_u32 s1, s1, 0x18000
	sl_mull_u32 s2, s21, 0x40
	sl_add_i32 s24, s2, s1
	sl_mov_b32 s25, s30
	sl_sme_load_16x1b64_col s[32:35], s[24:25], 0x0, 0x0, 0x0, 0x1
	sl_add_i32 s72, s24, 0x30000
	sl_mov_b32 s73, s30
	sl_sme_load_16x1b64_col s[32:35], s[72:73], 0x0, 0x0, 0x800, 0x1
	sl_sme_load_16x1b64_col s[32:35], s[24:25], 0x0, 0x2, 0x200, 0x1
	sl_sme_load_16x1b64_col s[32:35], s[72:73], 0x0, 0x2, 0xa00, 0x1
	.loc	1 37 45 is_stmt 1               ; candidate.py:37:45
	ml_shl_b32 v13, tid, 0x2
	ml_bfe2_b32 v10, tid, 0x44
	ml_and_b32 v14, tid, 0x38
	.loc	1 37 32 is_stmt 0               ; candidate.py:37:32
	ml_add_i32 v10, s74, v10
	ml_add_i32 v15, v10, 0x4
	ml_add_i32 v16, v10, 0x8
	ml_add_i32 v17, v10, 0xc
	ml_add_i32 v18, v10, 0x10
	ml_add_i32 v19, v10, 0x14
	ml_add_i32 v20, v10, 0x18
	ml_add_i32 v21, v10, 0x1c
	.loc	1 38 44 is_stmt 1               ; candidate.py:38:44
	ml_and_b32 v35, tid, 0xf
	sl_srl_b32 {s25, wcr}, s0, 0x2
	.loc	1 47 55                         ; candidate.py:47:55
	ml_cmp_lt_u32 tcr, v10, 0x7ee
	.loc	1 47 30 is_stmt 0               ; candidate.py:47:30
	ml_shl_b32 v22, v10, 0x4
	ml_shl_b32 v10, v10, 0x3
	ml_add_i32 v10, v22, v10
	.loc	1 47 55                         ; candidate.py:47:55
	sl_mov_b64 s[16:17], tcr
	ml_cmp_lt_u32 tcr, v15, 0x7ee
	.loc	1 47 30                         ; candidate.py:47:30
	ml_shl_b32 v22, v15, 0x4
	ml_shl_b32 v15, v15, 0x3
	ml_add_i32 v15, v22, v15
	.loc	1 47 55                         ; candidate.py:47:55
	sl_mov_b64 s[14:15], tcr
	ml_cmp_lt_u32 tcr, v16, 0x7ee
	.loc	1 47 30                         ; candidate.py:47:30
	ml_shl_b32 v22, v16, 0x4
	ml_shl_b32 v16, v16, 0x3
	ml_add_i32 v16, v22, v16
	.loc	1 47 55                         ; candidate.py:47:55
	sl_mov_b64 s[12:13], tcr
	ml_cmp_lt_u32 tcr, v17, 0x7ee
	.loc	1 47 30                         ; candidate.py:47:30
	ml_shl_b32 v22, v17, 0x4
	ml_shl_b32 v17, v17, 0x3
	ml_add_i32 v17, v22, v17
	.loc	1 47 55                         ; candidate.py:47:55
	sl_mov_b64 s[10:11], tcr
	ml_cmp_lt_u32 tcr, v18, 0x7ee
	.loc	1 47 30                         ; candidate.py:47:30
	ml_shl_b32 v22, v18, 0x4
	ml_shl_b32 v18, v18, 0x3
	ml_add_i32 v18, v22, v18
	.loc	1 47 55                         ; candidate.py:47:55
	sl_mov_b64 s[6:7], tcr
	ml_cmp_lt_u32 tcr, v19, 0x7ee
	.loc	1 47 30                         ; candidate.py:47:30
	ml_shl_b32 v22, v19, 0x4
	ml_shl_b32 v19, v19, 0x3
	ml_add_i32 v19, v22, v19
	.loc	1 47 55                         ; candidate.py:47:55
	sl_mov_b64 s[4:5], tcr
	ml_cmp_lt_u32 tcr, v20, 0x7ee
	.loc	1 47 30                         ; candidate.py:47:30
	ml_shl_b32 v22, v20, 0x4
	ml_shl_b32 v20, v20, 0x3
	ml_add_i32 v36, v22, v20
	.loc	1 47 55                         ; candidate.py:47:55
	sl_mov_b64 s[2:3], tcr
	ml_cmp_lt_u32 tcr, v21, 0x7ee
	.loc	1 47 30                         ; candidate.py:47:30
	ml_shl_b32 v20, v21, 0x4
	ml_shl_b32 v21, v21, 0x3
	ml_add_i32 v37, v20, v21
	.loc	1 47 55                         ; candidate.py:47:55
	sl_mov_b64 s[0:1], tcr
	.loc	1 47 26                         ; candidate.py:47:26
	ml_sra_b32 v20, v10, 0x1f
	ml_shl_b32 v21, v10, 0x2
	ml_shl_b32 v20, v20, 0x2
	ml_addo_u32 {v32, tcr}, s22, v21
	ml_srl_b32 v10, v10, 0x1e
	ml_or_b32 v10, v20, v10
	ml_mov_b32 v20, s23
	ml_addc_i32 v33, v20, v10, tcr
	ml_sra_b32 v10, v15, 0x1f
	ml_shl_b32 v20, v15, 0x2
	ml_shl_b32 v10, v10, 0x2
	ml_addo_u32 {v30, tcr}, s22, v20
	ml_srl_b32 v15, v15, 0x1e
	ml_or_b32 v10, v10, v15
	ml_mov_b32 v15, s23
	ml_addc_i32 v31, v15, v10, tcr
	ml_sra_b32 v10, v16, 0x1f
	ml_shl_b32 v15, v16, 0x2
	ml_shl_b32 v10, v10, 0x2
	ml_addo_u32 {v28, tcr}, s22, v15
	ml_srl_b32 v15, v16, 0x1e
	ml_or_b32 v10, v10, v15
	ml_mov_b32 v15, s23
	ml_addc_i32 v29, v15, v10, tcr
	ml_sra_b32 v10, v17, 0x1f
	ml_shl_b32 v15, v17, 0x2
	ml_shl_b32 v10, v10, 0x2
	ml_addo_u32 {v26, tcr}, s22, v15
	ml_srl_b32 v15, v17, 0x1e
	ml_or_b32 v10, v10, v15
	ml_mov_b32 v15, s23
	ml_addc_i32 v27, v15, v10, tcr
	ml_sra_b32 v10, v18, 0x1f
	ml_shl_b32 v15, v18, 0x2
	ml_shl_b32 v10, v10, 0x2
	ml_addo_u32 {v24, tcr}, s22, v15
	ml_srl_b32 v15, v18, 0x1e
	ml_or_b32 v10, v10, v15
	ml_mov_b32 v15, s23
	ml_addc_i32 v25, v15, v10, tcr
	ml_sra_b32 v10, v19, 0x1f
	ml_shl_b32 v15, v19, 0x2
	ml_shl_b32 v10, v10, 0x2
	ml_addo_u32 {v22, tcr}, s22, v15
	ml_srl_b32 v15, v19, 0x1e
	ml_or_b32 v10, v10, v15
	ml_mov_b32 v15, s23
	ml_addc_i32 v23, v15, v10, tcr
	ml_sra_b32 v10, v36, 0x1f
	ml_shl_b32 v15, v36, 0x2
	ml_shl_b32 v10, v10, 0x2
	ml_addo_u32 {v20, tcr}, s22, v15
	ml_srl_b32 v15, v36, 0x1e
	ml_or_b32 v10, v10, v15
	ml_mov_b32 v15, s23
	ml_addc_i32 v21, v15, v10, tcr
	ml_sra_b32 v10, v37, 0x1f
	ml_shl_b32 v15, v37, 0x2
	ml_shl_b32 v10, v10, 0x2
	ml_addo_u32 {v18, tcr}, s22, v15
	ml_srl_b32 v15, v37, 0x1e
	ml_or_b32 v10, v10, v15
	ml_mov_b32 v15, s23
	ml_addc_i32 v19, v15, v10, tcr
	.loc	1 38 31 is_stmt 1               ; candidate.py:38:31
	sl_add_i32 s22, s20, s25
	ml_add_i32 v10, s22, v35
	.loc	1 41 23                         ; candidate.py:41:23
	ml_mad_u32_u16 v43, 24, v10, 0
	.loc	1 43 20                         ; candidate.py:43:20
	sl_wait vmcnt(0)
	ml_and_b32 v72, v12, 0xff
	ml_bfe2_b32 v75, v12, 0x108
	ml_bfe2_b32 v76, v12, 0x110
	ml_bfe2_b32 v77, v12, 0x118
	ml_shl_b32 v12, v14, 0x6
	ml_shl_b32 v14, v8, 0x3
	ml_and_b32 v15, tid, 0x4
	ml_cmp_eq_u32 tcr, v15, 0x0
	ml_mov_b32 v15, 0x140
	ml_csel_b32 v15, 0, v15, tcr
	sl_srl_b32 {s20, wcr}, s38, 0x2
	sl_and_b32 {s20, wcr}, s20, 0x20
	ml_add_i32 v15, s20, v15
	ml_anyop3_b32 v12, v12, v14, 24, 0xffffffea
	ml_anyop3_b32 v42, v15, v12, s21, 0xfffffffe
	ml_xor_b32 v41, v42, 0x40
	ml_shl_b32 v12, v35, 0x1
	sl_mov_b32 s20, 0xc0
	ml_anyop3_b32 v35, s20, v13, v12, 0xf8
	ml_xor_b32 v36, v35, 0x40
	ml_shl_b32 v12, v8, 0x6
	sl_mov_b32 s20, 0x3300
	ml_anyop3_b32 v40, v7, v12, s20, 0xffffffea
	ml_xor_b32 v39, v40, 0x10
	ml_xor_b32 v38, v40, 0x20
	ml_xor_b32 v37, v40, 0x30
	.loc	1 41 23                         ; candidate.py:41:23
	ml_add_i32 v44, v11, 0x40
	sl_sub_u64 s[34:35], s[8:9], s[8:9]
	sl_mov_b32 s81, 0x504
	sl_mov_b32 s82, 0x60504
	sl_mov_b32 s23, 0xfff00004
	sl_mov_b32 s83, 0x8000
	sl_mov_b32 s84, 0x9000
	sl_mov_b32 s85, 0x8400
	sl_mov_b32 s86, 0x8800
	sl_mov_b32 s87, 0x8c00
	sl_mov_b32 s88, 0x9400
	sl_mov_b32 s89, 0x9800
	sl_mov_b32 s90, 0x9c00
	sl_mov_b32 s91, s70
	ml_mov_b32 v11, 0x0
	ml_mov_b32 v12, 0x0
	ml_mov_b32 v13, 0x0
	ml_mov_b32 v14, 0x0
	ml_mov_b32 v15, 0x0
	ml_mov_b32 v16, 0x0
	ml_mov_b32 v17, 0x0
	sl_jump BB0_17
BB0_16:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 0 0 is_stmt 0                 ; candidate.py:0
	sl_add_i64 s[34:35], s[34:35], 0x1
	sl_shl_b64 {s[20:21], wcr}, s[34:35], 0x8
	.loc	1 41 23 is_stmt 1               ; candidate.py:41:23
	sl_add_i32 s25, s31, 0x1
	sl_cmp_lt_i32 wcr, s25, 0x2
	sl_csel_b32 s31, s25, 0x0, wcr
	.loc	1 45 41                         ; candidate.py:45:41
	sl_add_i64 s[68:69], s[32:33], s[20:21]
	.loc	1 45 20 is_stmt 0               ; candidate.py:45:20
	sl_mull_u32 s20, s31, 0x4000
	sl_add_i32 s25, s20, s30
	sl_sme_load_16x1b64_col s[68:71], s[24:25], 0x0, 0x0, 0x0, 0x1
	sl_mov_b32 s73, s25
	sl_sme_load_16x1b64_col s[68:71], s[72:73], 0x0, 0x0, 0x800, 0x1
	sl_sme_load_16x1b64_col s[68:71], s[24:25], 0x0, 0x2, 0x200, 0x1
	sl_sme_load_16x1b64_col s[68:71], s[72:73], 0x0, 0x2, 0xa00, 0x1
	.loc	1 43 20 is_stmt 1               ; candidate.py:43:20
	sl_wait vmcnt(0)
	ml_and_b32 v56, v74, 0xff
	ml_bfe2_b32 v55, v74, 0x108
	ml_bfe2_b32 v54, v74, 0x110
	ml_bfe2_b32 v53, v74, 0x118
	ml_and_b32 v45, v69, 0xff
	ml_bfe2_b32 v46, v69, 0x108
	ml_bfe2_b32 v47, v69, 0x110
	ml_bfe2_b32 v48, v69, 0x118
	ml_and_b32 v52, v73, 0xff
	ml_bfe2_b32 v51, v73, 0x108
	ml_bfe2_b32 v50, v73, 0x110
	ml_bfe2_b32 v49, v73, 0x118
	.loc	1 50 28                         ; candidate.py:50:28
	ml_cvt_f32_i32  v4, v4
	ml_cvt_f32_i32  v5, v5
	ml_cvt_f32_i32  v62, v6
	ml_cvt_f32_i32  v7, v7
	ml_cvt_f32_i32  v64, v0
	ml_cvt_f32_i32  v76, v1
	ml_cvt_f32_i32  v77, v2
	ml_cvt_f32_i32  v78, v3
	.loc	1 43 20                         ; candidate.py:43:20
	ml_and_b32 v0, v67, 0xff
	ml_bfe2_b32 v1, v67, 0x108
	ml_bfe2_b32 v2, v67, 0x110
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v3, v58, v75
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v9, v3, v4, v9
	.loc	1 43 20                         ; candidate.py:43:20
	ml_bfe2_b32 v3, v67, 0x118
	ml_and_b32 v4, v70, 0xff
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v6, v57, v75
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v11, v6, v5, v11
	.loc	1 43 20                         ; candidate.py:43:20
	ml_bfe2_b32 v6, v70, 0x108
	ml_bfe2_b32 v5, v70, 0x110
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v57, v60, v75
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v12, v57, v62, v12
	.loc	1 43 20                         ; candidate.py:43:20
	ml_bfe2_b32 v57, v70, 0x118
	ml_and_b32 v58, v66, 0xff
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v59, v59, v75
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v13, v59, v7, v13
	.loc	1 43 20                         ; candidate.py:43:20
	ml_bfe2_b32 v59, v66, 0x108
	ml_bfe2_b32 v60, v66, 0x110
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v7, v61, v75
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v14, v7, v64, v14
	.loc	1 43 20                         ; candidate.py:43:20
	ml_bfe2_b32 v61, v66, 0x118
	ml_and_b32 v62, v68, 0xff
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v7, v63, v75
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v15, v7, v76, v15
	.loc	1 43 20                         ; candidate.py:43:20
	ml_bfe2_b32 v64, v68, 0x108
	ml_bfe2_b32 v63, v68, 0x110
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v7, v72, v75
	ml_mul_f32 v72, v65, v75
	.loc	1 43 20                         ; candidate.py:43:20
	ml_bfe2_b32 v65, v68, 0x118
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v16, v7, v77, v16
	ml_fma_f32 v17, v72, v78, v17
	.loc	1 43 20                         ; candidate.py:43:20
	ml_and_b32 v72, v71, 0xff
	ml_bfe2_b32 v75, v71, 0x108
	ml_bfe2_b32 v76, v71, 0x110
	ml_bfe2_b32 v77, v71, 0x118
	.loc	1 41 23                         ; candidate.py:41:23
	sl_xor_b64 {s[20:21], wcr}, s[34:35], 0x17
	ml_add_i32 v44, v44, 0x40
	sl_cbr_wcrz BB0_49, wcr
BB0_17:                                 ; =>This Inner Loop Header: Depth=1
	sl_add_i32 s20, s91, 0x1
	sl_cmp_lt_i32 wcr, s20, 0x2
	sl_csel_b32 s91, s20, 0x0, wcr
	.loc	1 45 20                         ; candidate.py:45:20
	sl_wait g2scnt(0)
	sl_barrier_req 0x0
	sl_barrier_wait 0x0
	.loc	1 43 20                         ; candidate.py:43:20
	ml_slb_store_b8  v62, v42, s83, #0, null
	.loc	1 45 20                         ; candidate.py:45:20
	sl_mull_u32 s20, s91, 0x4000
	.loc	1 43 20                         ; candidate.py:43:20
	ml_slb_store_b8  v64, v42, s83, #2, null
	ml_slb_store_b8  v63, v42, s83, #4, null
	ml_slb_store_b8  v65, v42, s83, #6, null
	ml_slb_store_b8  v4, v42, s83, #128, null
	ml_slb_store_b8  v6, v42, s83, #130, null
	ml_slb_store_b8  v5, v42, s83, #132, null
	ml_slb_store_b8  v57, v42, s83, #134, null
	ml_slb_store_b8  v52, v42, s84, #0, null
	ml_slb_store_b8  v51, v42, s84, #2, null
	ml_slb_store_b8  v50, v42, s84, #4, null
	ml_slb_store_b8  v49, v42, s84, #6, null
	ml_slb_store_b8  v56, v42, s84, #128, null
	ml_slb_store_b8  v55, v42, s84, #130, null
	ml_slb_store_b8  v54, v42, s84, #132, null
	ml_slb_store_b8  v53, v42, s84, #134, null
	ml_slb_store_b8  v58, v41, s83, #0, null
	ml_slb_store_b8  v59, v41, s83, #2, null
	ml_slb_store_b8  v60, v41, s83, #4, null
	ml_slb_store_b8  v61, v41, s83, #6, null
	ml_slb_store_b8  v0, v41, s83, #128, null
	ml_slb_store_b8  v1, v41, s83, #130, null
	ml_slb_store_b8  v2, v41, s83, #132, null
	ml_slb_store_b8  v3, v41, s83, #134, null
	ml_slb_store_b8  v45, v41, s84, #0, null
	ml_slb_store_b8  v46, v41, s84, #2, null
	ml_slb_store_b8  v47, v41, s84, #4, null
	ml_slb_store_b8  v48, v41, s84, #6, null
	ml_slb_store_b8  v72, v41, s84, #128, null
	ml_slb_store_b8  v75, v41, s84, #130, null
	ml_slb_store_b8  v76, v41, s84, #132, null
	ml_slb_store_b8  v77, v41, s84, #134, null
	sl_wait lmcnt(0)
	sl_barrier 
	.loc	1 45 20                         ; candidate.py:45:20
	ml_slb_load_b32x1  v45, v40, s20, #0, null
	sl_add_i32 s21, s20, 0x400
	sl_add_i32 s25, s20, 0x800
	sl_add_i32 s38, s20, 0xc00
	ml_slb_load_b32x1  v47, v40, s21, #0, null
	ml_slb_load_b32x1  v49, v40, s25, #0, null
	ml_slb_load_b32x1  v51, v40, s38, #0, null
	ml_slb_load_b32x1  v46, v39, s20, #0, null
	ml_slb_load_b32x1  v48, v39, s21, #0, null
	ml_slb_load_b32x1  v50, v39, s25, #0, null
	ml_slb_load_b32x1  v52, v39, s38, #0, null
	ml_slb_load_b32x1  v53, v38, s20, #0, null
	ml_slb_load_b32x1  v55, v38, s21, #0, null
	ml_slb_load_b32x1  v57, v38, s25, #0, null
	ml_slb_load_b32x1  v59, v38, s38, #0, null
	ml_slb_load_b32x1  v54, v37, s20, #0, null
	ml_slb_load_b32x1  v56, v37, s21, #0, null
	ml_slb_load_b32x1  v58, v37, s25, #0, null
	ml_slb_load_b32x1  v60, v37, s38, #0, null
	.loc	1 46 25                         ; candidate.py:46:25
	ml_slb_load_b8  v0, v36, s83, #256, null
	ml_slb_load_b8  v1, v36, s83, #257, null
	ml_slb_load_b8  v2, v36, s83, #288, null
	ml_slb_load_b8  v3, v36, s83, #289, null
	ml_slb_load_b8  v4, v35, s83, #0, null
	ml_slb_load_b8  v5, v35, s83, #1, null
	ml_slb_load_b8  v6, v35, s83, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v1, v0, 4
	ml_slb_load_b8  v7, v35, s83, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v2, v0, s81
	ml_slb_load_b8  v63, v36, s83, #768, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v62, v3, v0, s82
	ml_slb_load_b8  v64, v36, s83, #769, null
	ml_slb_load_b8  v65, v36, s83, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v4, v5, v4, 4
	ml_slb_load_b8  v66, v36, s83, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v4, v6, v4, s81
	ml_slb_load_b8  v67, v35, s83, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v61, v7, v4, s82
	ml_slb_load_b8  v68, v35, s83, #513, null
	ml_slb_load_b8  v69, v35, s83, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v63, v64, v63, 4
	ml_slb_load_b8  v70, v35, s83, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v63, v65, v63, s81
	ml_slb_load_b8  v71, v36, s85, #256, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v64, v66, v63, s82
	ml_slb_load_b8  v72, v36, s85, #257, null
	ml_slb_load_b8  v73, v36, s85, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v63, v68, v67, 4
	ml_slb_load_b8  v74, v36, s85, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v63, v69, v63, s81
	ml_slb_load_b8  v75, v35, s85, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v63, v70, v63, s82
	ml_slb_load_b8  v76, v35, s85, #1, null
	ml_slb_load_b8  v77, v35, s85, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v65, v72, v71, 4
	ml_slb_load_b8  v78, v35, s85, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v65, v73, v65, s81
	ml_slb_load_b8  v79, v36, s85, #768, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v66, v74, v65, s82
	ml_slb_load_b8  v80, v36, s85, #769, null
	ml_slb_load_b8  v81, v36, s85, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v65, v76, v75, 4
	ml_slb_load_b8  v82, v36, s85, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v65, v77, v65, s81
	ml_slb_load_b8  v0, v35, s85, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v65, v78, v65, s82
	ml_slb_load_b8  v1, v35, s85, #513, null
	ml_slb_load_b8  v2, v35, s85, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v67, v80, v79, 4
	ml_slb_load_b8  v3, v35, s85, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v67, v81, v67, s81
	ml_slb_load_b8  v4, v36, s86, #256, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v68, v82, v67, s82
	ml_slb_load_b8  v5, v36, s86, #257, null
	ml_slb_load_b8  v6, v36, s86, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v1, v0, 4
	ml_slb_load_b8  v7, v36, s86, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v2, v0, s81
	ml_slb_load_b8  v83, v35, s86, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v67, v3, v0, s82
	ml_slb_load_b8  v84, v35, s86, #1, null
	ml_slb_load_b8  v85, v35, s86, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v4, v5, v4, 4
	ml_slb_load_b8  v86, v35, s86, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v4, v6, v4, s81
	ml_slb_load_b8  v87, v36, s86, #768, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v70, v7, v4, s82
	ml_slb_load_b8  v88, v36, s86, #769, null
	ml_slb_load_b8  v89, v36, s86, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v69, v84, v83, 4
	ml_slb_load_b8  v90, v36, s86, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v69, v85, v69, s81
	ml_slb_load_b8  v71, v35, s86, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v69, v86, v69, s82
	ml_slb_load_b8  v73, v35, s86, #513, null
	ml_slb_load_b8  v74, v35, s86, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v72, v88, v87, 4
	ml_slb_load_b8  v91, v35, s86, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v72, v89, v72, s81
	ml_slb_load_b8  v75, v36, s87, #256, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v72, v90, v72, s82
	ml_slb_load_b8  v76, v36, s87, #257, null
	ml_slb_load_b8  v77, v36, s87, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v71, v73, v71, 4
	ml_slb_load_b8  v78, v36, s87, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v71, v74, v71, s81
	ml_slb_load_b8  v79, v35, s87, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v71, v91, v71, s82
	ml_slb_load_b8  v80, v35, s87, #1, null
	ml_slb_load_b8  v81, v35, s87, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v73, v76, v75, 4
	ml_slb_load_b8  v82, v35, s87, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v73, v77, v73, s81
	ml_slb_load_b8  v0, v36, s87, #768, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v74, v78, v73, s82
	ml_slb_load_b8  v1, v36, s87, #769, null
	ml_slb_load_b8  v2, v36, s87, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v73, v80, v79, 4
	ml_slb_load_b8  v3, v36, s87, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v73, v81, v73, s81
	ml_slb_load_b8  v4, v35, s87, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v73, v82, v73, s82
	ml_slb_load_b8  v5, v35, s87, #513, null
	ml_slb_load_b8  v6, v35, s87, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v1, v0, 4
	ml_mov_b32 v1, v34
	ml_slb_load_b8  v7, v35, s87, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v2, v0, s81
	ml_mov_b32 v2, v34
	ml_slb_load_b8  v83, v36, s84, #256, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v76, v3, v0, s82
	ml_mov_b32 v3, v34
	ml_slb_load_b8  v84, v36, s84, #257, null
	ml_slb_load_b8  v85, v36, s84, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v5, v4, 4
	ml_slb_load_b8  v86, v36, s84, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v6, v0, s81
	ml_slb_load_b8  v87, v35, s84, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v75, v7, v0, s82
	ml_slb_load_b8  v88, v35, s84, #1, null
	ml_slb_load_b8  v89, v35, s84, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v84, v83, 4
	ml_slb_load_b8  v90, v35, s84, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v85, v0, s81
	ml_slb_load_b8  v91, v36, s84, #768, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v78, v86, v0, s82
	ml_slb_load_b8  v92, v36, s84, #769, null
	ml_slb_load_b8  v93, v36, s84, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v88, v87, 4
	ml_slb_load_b8  v94, v36, s84, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v89, v0, s81
	ml_slb_load_b8  v95, v35, s84, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v77, v90, v0, s82
	ml_mov_b32 v0, 0x0
	ml_slb_load_b8  v96, v35, s84, #513, null
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[61:62], v[45:46], v[0:3]
	ml_slb_load_b8  v97, v35, s84, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v61, v92, v91, 4
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[77:78], v[45:46], v[0:3]
	ml_slb_load_b8  v98, v35, s84, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v61, v93, v61, s81
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[63:64], v[53:54], v[4:7]
	ml_slb_load_b8  v79, v36, s88, #256, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v62, v94, v61, s82
	ml_slb_load_b8  v80, v36, s88, #257, null
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[65:66], v[47:48], v[4:7]
	ml_slb_load_b8  v81, v36, s88, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v96, v95, 4
	sl_wait lmcnt(4)
	ml_byte_permute_b32 v45, v97, v45, s81
	ml_slb_load_b8  v82, v36, s88, #289, null
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[67:68], v[55:56], v[4:7]
	ml_slb_load_b8  v99, v35, s88, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v61, v98, v45, s82
	ml_slb_load_b8  v100, v35, s88, #1, null
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[61:62], v[53:54], v[0:3]
	ml_slb_load_b8  v101, v35, s88, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v80, v79, 4
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[69:70], v[49:50], v[4:7]
	ml_slb_load_b8  v102, v35, s88, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v81, v45, s81
	ml_slb_load_b8  v103, v36, s88, #768, null
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[71:72], v[57:58], v[4:7]
	ml_slb_load_b8  v104, v36, s88, #769, null
	ml_slb_load_b8  v105, v36, s88, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v46, v100, v99, 4
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[73:74], v[51:52], v[4:7]
	ml_slb_load_b8  v106, v36, s88, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v62, v101, v46, s81
	ml_byte_permute_b32 v46, v82, v45, s82
	ml_slb_load_b8  v83, v35, s88, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v102, v62, s82
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[75:76], v[59:60], v[4:7]
	ml_slb_load_b8  v84, v35, s88, #513, null
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[45:46], v[47:48], v[0:3]
	ml_slb_load_b8  v85, v35, s88, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v104, v103, 4
	ml_slb_load_b8  v86, v35, s88, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v105, v45, s81
	ml_slb_load_b8  v87, v36, s89, #256, null
	ml_slb_load_b8  v88, v36, s89, #257, null
	ml_slb_load_b8  v89, v36, s89, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v46, v84, v83, 4
	ml_slb_load_b8  v90, v36, s89, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v66, v85, v46, s81
	ml_byte_permute_b32 v46, v106, v45, s82
	ml_slb_load_b8  v91, v35, s89, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v86, v66, s82
	ml_slb_load_b8  v77, v35, s89, #1, null
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[45:46], v[55:56], v[0:3]
	ml_slb_load_b8  v63, v35, s89, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v88, v87, 4
	ml_slb_load_b8  v64, v35, s89, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v89, v45, s81
	ml_slb_load_b8  v78, v36, s89, #768, null
	ml_slb_load_b8  v53, v36, s89, #769, null
	ml_slb_load_b8  v54, v36, s89, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v46, v77, v91, 4
	ml_slb_load_b8  v61, v36, s89, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v63, v63, v46, s81
	ml_byte_permute_b32 v46, v90, v45, s82
	ml_slb_load_b8  v62, v35, s89, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v64, v63, s82
	ml_slb_load_b8  v47, v35, s89, #513, null
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[45:46], v[49:50], v[0:3]
	ml_slb_load_b8  v48, v35, s89, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v53, v78, 4
	ml_slb_load_b8  v65, v35, s89, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v54, v45, s81
	ml_slb_load_b8  v67, v36, s90, #256, null
	ml_slb_load_b8  v66, v36, s90, #257, null
	ml_slb_load_b8  v55, v36, s90, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v46, v47, v62, 4
	ml_slb_load_b8  v56, v36, s90, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v47, v48, v46, s81
	ml_byte_permute_b32 v46, v61, v45, s82
	ml_slb_load_b8  v68, v35, s90, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v65, v47, s82
	ml_slb_load_b8  v63, v35, s90, #1, null
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[45:46], v[57:58], v[0:3]
	ml_slb_load_b8  v49, v35, s90, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v66, v67, 4
	ml_mov_b32 v58, 0x0
	ml_slb_load_b8  v50, v35, s90, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v55, v45, s81
	ml_slb_load_b8  v53, v36, s90, #768, null
	ml_slb_load_b8  v48, v36, s90, #769, null
	ml_slb_load_b8  v47, v36, s90, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v46, v63, v68, 4
	ml_slb_load_b8  v54, v36, s90, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v49, v49, v46, s81
	ml_byte_permute_b32 v46, v56, v45, s82
	ml_slb_load_b8  v57, v35, s90, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v45, v50, v49, s82
	ml_slb_load_b8  v55, v35, s90, #513, null
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[45:46], v[51:52], v[0:3]
	ml_slb_load_b8  v49, v35, s90, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v46, v48, v53, 4
	ml_slb_load_b8  v45, v35, s90, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v46, v47, v46, s81
	sl_wait lmcnt(4)
	ml_byte_permute_b32 v46, v54, v46, s82
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v47, v55, v57, 4
	.loc	1 47 21                         ; candidate.py:47:21
	ml_mov_b32 v57, 0x0
	.loc	1 46 25                         ; candidate.py:46:25
	sl_wait lmcnt(1)
	ml_byte_permute_b32 v47, v49, v47, s81
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v45, v45, v47, s82
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[45:46], v[59:60], v[0:3]
	.loc	1 47 21                         ; candidate.py:47:21
	sl_and_savetmsk_b64 {s[20:21], wcr}, s[16:17], tmsk
	; mask branch BB0_19
BB0_18:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 0 21 is_stmt 0                ; candidate.py:0:21
	sl_shl_b64 {s[38:39], wcr}, s[34:35], 0x2
	ml_addo_u32 {v45, tcr}, s38, v32
	ml_mov_b32 v46, s39
	ml_addc_i32 v46, v33, v46, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v58, v[45:46], kop=0
BB0_19:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[20:21]
	.loc	1 47 21                         ; candidate.py:47:21
	sl_and_savetmsk_b64 {s[20:21], wcr}, s[14:15], tmsk
	; mask branch BB0_21
BB0_20:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 47 39                         ; candidate.py:47:39
	sl_shl_b64 {s[38:39], wcr}, s[34:35], 0x2
	ml_addo_u32 {v45, tcr}, s38, v30
	ml_mov_b32 v46, s39
	ml_addc_i32 v46, v31, v46, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v57, v[45:46], kop=0
BB0_21:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[20:21]
	.loc	1 47 21                         ; candidate.py:47:21
	ml_mov_b32 v59, 0x0
	ml_mov_b32 v60, 0x0
	sl_and_savetmsk_b64 {s[20:21], wcr}, s[12:13], tmsk
	; mask branch BB0_23
BB0_22:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 47 39                         ; candidate.py:47:39
	sl_shl_b64 {s[38:39], wcr}, s[34:35], 0x2
	ml_addo_u32 {v45, tcr}, s38, v28
	ml_mov_b32 v46, s39
	ml_addc_i32 v46, v29, v46, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v60, v[45:46], kop=0
BB0_23:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[20:21]
	.loc	1 47 21                         ; candidate.py:47:21
	sl_and_savetmsk_b64 {s[20:21], wcr}, s[10:11], tmsk
	; mask branch BB0_25
BB0_24:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 47 39                         ; candidate.py:47:39
	sl_shl_b64 {s[38:39], wcr}, s[34:35], 0x2
	ml_addo_u32 {v45, tcr}, s38, v26
	ml_mov_b32 v46, s39
	ml_addc_i32 v46, v27, v46, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v59, v[45:46], kop=0
BB0_25:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[20:21]
	.loc	1 47 21                         ; candidate.py:47:21
	ml_mov_b32 v63, 0x0
	ml_mov_b32 v61, 0x0
	sl_and_savetmsk_b64 {s[20:21], wcr}, s[6:7], tmsk
	; mask branch BB0_27
BB0_26:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 47 39                         ; candidate.py:47:39
	sl_shl_b64 {s[38:39], wcr}, s[34:35], 0x2
	ml_addo_u32 {v45, tcr}, s38, v24
	ml_mov_b32 v46, s39
	ml_addc_i32 v46, v25, v46, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v61, v[45:46], kop=0
BB0_27:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[20:21]
	.loc	1 47 21                         ; candidate.py:47:21
	sl_and_savetmsk_b64 {s[20:21], wcr}, s[4:5], tmsk
	; mask branch BB0_29
BB0_28:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 47 39                         ; candidate.py:47:39
	sl_shl_b64 {s[38:39], wcr}, s[34:35], 0x2
	ml_addo_u32 {v45, tcr}, s38, v22
	ml_mov_b32 v46, s39
	ml_addc_i32 v46, v23, v46, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v63, v[45:46], kop=0
BB0_29:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[20:21]
	.loc	1 47 21                         ; candidate.py:47:21
	ml_mov_b32 v65, 0x0
	ml_mov_b32 v72, 0x0
	sl_and_savetmsk_b64 {s[20:21], wcr}, s[2:3], tmsk
	; mask branch BB0_31
BB0_30:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 47 39                         ; candidate.py:47:39
	sl_shl_b64 {s[38:39], wcr}, s[34:35], 0x2
	ml_addo_u32 {v45, tcr}, s38, v20
	ml_mov_b32 v46, s39
	ml_addc_i32 v46, v21, v46, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v72, v[45:46], kop=0
BB0_31:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[20:21]
	.loc	1 47 21                         ; candidate.py:47:21
	sl_and_savetmsk_b64 {s[20:21], wcr}, s[0:1], tmsk
	; mask branch BB0_33
BB0_32:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 47 39                         ; candidate.py:47:39
	sl_shl_b64 {s[38:39], wcr}, s[34:35], 0x2
	ml_addo_u32 {v45, tcr}, s38, v18
	ml_mov_b32 v46, s39
	ml_addc_i32 v46, v19, v46, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v65, v[45:46], kop=0
BB0_33:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[20:21]
	.loc	1 48 39 is_stmt 1               ; candidate.py:48:39
	sl_shl_b64 {s[20:21], wcr}, s[34:35], 0x2
	.loc	1 48 21 is_stmt 0               ; candidate.py:48:21
	sl_add_i64 s[20:21], s[26:27], s[20:21]
	ml_lsa_load_dword v75, s[20:23], unsigned v43, noreg, #0, ca|mie
	.loc	1 43 20 is_stmt 1               ; candidate.py:43:20
	ml_mov_b32 v66, 0x0
	sl_or_b32 {s18, wcr}, s18, 0x0
	ml_mov_b32 v68, 0x0
	sl_cbr_wcrz BB0_35, wcr
; %bb.34:                               ;   in Loop: Header=BB0_17 Depth=1
	sl_mov_b64 s[38:39], s[22:23]
	ml_lsa_load_dword v68, s[36:39], unsigned v44, noreg, #0, ca|mie
BB0_35:                                 ;   in Loop: Header=BB0_17 Depth=1
	sl_or_b32 {s19, wcr}, s19, 0x0
	sl_cbr_wcrz BB0_37, wcr
; %bb.36:                               ;   in Loop: Header=BB0_17 Depth=1
	sl_mov_b64 s[42:43], s[22:23]
	ml_lsa_load_dword v66, s[40:43], unsigned v44, noreg, #0, ca|mie
BB0_37:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 44 38                         ; candidate.py:44:38
	sl_cmp_lt_u32 wcr, s75, 0x7ee
	.loc	1 43 20                         ; candidate.py:43:20
	ml_mov_b32 v67, 0x0
	ml_mov_b32 v70, 0x0
	sl_cbr_wcrz BB0_39, wcr
; %bb.38:                               ;   in Loop: Header=BB0_17 Depth=1
	sl_mov_b64 s[46:47], s[22:23]
	ml_lsa_load_dword v70, s[44:47], unsigned v44, noreg, #0, ca|mie
BB0_39:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 44 38                         ; candidate.py:44:38
	sl_cmp_lt_u32 wcr, s76, 0x7ee
	.loc	1 43 20                         ; candidate.py:43:20
	sl_cbr_wcrz BB0_41, wcr
; %bb.40:                               ;   in Loop: Header=BB0_17 Depth=1
	sl_mov_b64 s[50:51], s[22:23]
	ml_lsa_load_dword v67, s[48:51], unsigned v44, noreg, #0, ca|mie
BB0_41:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 44 38                         ; candidate.py:44:38
	sl_cmp_lt_u32 wcr, s77, 0x7ee
	.loc	1 43 20                         ; candidate.py:43:20
	ml_mov_b32 v69, 0x0
	ml_mov_b32 v73, 0x0
	sl_cbr_wcrz BB0_43, wcr
; %bb.42:                               ;   in Loop: Header=BB0_17 Depth=1
	sl_mov_b64 s[54:55], s[22:23]
	ml_lsa_load_dword v73, s[52:55], unsigned v44, noreg, #0, ca|mie
BB0_43:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 44 38                         ; candidate.py:44:38
	sl_cmp_lt_u32 wcr, s78, 0x7ee
	.loc	1 43 20                         ; candidate.py:43:20
	sl_cbr_wcrz BB0_45, wcr
; %bb.44:                               ;   in Loop: Header=BB0_17 Depth=1
	sl_mov_b64 s[58:59], s[22:23]
	ml_lsa_load_dword v69, s[56:59], unsigned v44, noreg, #0, ca|mie
BB0_45:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 44 38                         ; candidate.py:44:38
	sl_cmp_lt_u32 wcr, s79, 0x7ee
	.loc	1 43 20                         ; candidate.py:43:20
	ml_mov_b32 v71, 0x0
	ml_mov_b32 v74, 0x0
	sl_cbr_wcrz BB0_47, wcr
; %bb.46:                               ;   in Loop: Header=BB0_17 Depth=1
	sl_mov_b64 s[62:63], s[22:23]
	ml_lsa_load_dword v74, s[60:63], unsigned v44, noreg, #0, ca|mie
BB0_47:                                 ;   in Loop: Header=BB0_17 Depth=1
	.loc	1 44 38                         ; candidate.py:44:38
	sl_cmp_lt_u32 wcr, s80, 0x7ee
	.loc	1 43 20                         ; candidate.py:43:20
	sl_cbr_wcrz BB0_16, wcr
; %bb.48:                               ;   in Loop: Header=BB0_17 Depth=1
	sl_mov_b64 s[66:67], s[22:23]
	ml_lsa_load_dword v71, s[64:67], unsigned v44, noreg, #0, ca|mie
	sl_jump BB0_16
BB0_49:                                 ; %.peel.begin
	.loc	1 41 23                         ; candidate.py:41:23
	sl_add_i32 s20, s91, 0x1
	.loc	1 45 20                         ; candidate.py:45:20
	sl_wait g2scnt(0)
	sl_barrier_req 0x0
	sl_barrier_wait 0x0
	.loc	1 43 20                         ; candidate.py:43:20
	sl_mov_b32 s18, 0x8000
	ml_slb_store_b8  v68, v42, s18, #0, null
	ml_srl_b32 v0, v68, 0x8
	sl_mov_b32 s19, 0x9000
	.loc	1 45 20                         ; candidate.py:45:20
	sl_mull_u32 s21, s20, 0x4000
	.loc	1 43 20                         ; candidate.py:43:20
	ml_slb_store_b8  v0, v42, s18, #2, null
	ml_srl_b32 v0, v68, 0x10
	.loc	1 41 23                         ; candidate.py:41:23
	sl_cmp_lt_i32 wcr, s20, 0x2
	sl_csel_b32 s20, s21, 0x0, wcr
	.loc	1 43 20                         ; candidate.py:43:20
	ml_slb_store_b8  v0, v42, s18, #4, null
	ml_srl_b32 v0, v68, 0x18
	ml_slb_store_b8  v0, v42, s18, #6, null
	ml_srl_b32 v0, v70, 0x8
	ml_slb_store_b8  v70, v42, s18, #128, null
	ml_slb_store_b8  v0, v42, s18, #130, null
	ml_srl_b32 v0, v70, 0x10
	ml_slb_store_b8  v0, v42, s18, #132, null
	ml_srl_b32 v0, v70, 0x18
	ml_slb_store_b8  v0, v42, s18, #134, null
	ml_srl_b32 v0, v73, 0x8
	ml_slb_store_b8  v73, v42, s19, #0, null
	ml_slb_store_b8  v0, v42, s19, #2, null
	ml_srl_b32 v0, v73, 0x10
	ml_slb_store_b8  v0, v42, s19, #4, null
	ml_srl_b32 v0, v73, 0x18
	ml_slb_store_b8  v0, v42, s19, #6, null
	ml_srl_b32 v0, v74, 0x8
	ml_slb_store_b8  v74, v42, s19, #128, null
	ml_slb_store_b8  v0, v42, s19, #130, null
	ml_srl_b32 v0, v74, 0x10
	ml_slb_store_b8  v0, v42, s19, #132, null
	ml_srl_b32 v0, v74, 0x18
	ml_slb_store_b8  v0, v42, s19, #134, null
	ml_srl_b32 v0, v66, 0x8
	ml_slb_store_b8  v66, v41, s18, #0, null
	ml_slb_store_b8  v0, v41, s18, #2, null
	ml_srl_b32 v0, v66, 0x10
	ml_slb_store_b8  v0, v41, s18, #4, null
	ml_srl_b32 v0, v66, 0x18
	ml_slb_store_b8  v0, v41, s18, #6, null
	ml_srl_b32 v0, v67, 0x8
	ml_slb_store_b8  v67, v41, s18, #128, null
	ml_slb_store_b8  v0, v41, s18, #130, null
	ml_srl_b32 v0, v67, 0x10
	ml_slb_store_b8  v0, v41, s18, #132, null
	ml_srl_b32 v0, v67, 0x18
	ml_slb_store_b8  v0, v41, s18, #134, null
	ml_srl_b32 v0, v69, 0x8
	ml_slb_store_b8  v69, v41, s19, #0, null
	ml_slb_store_b8  v0, v41, s19, #2, null
	ml_srl_b32 v0, v69, 0x10
	ml_slb_store_b8  v0, v41, s19, #4, null
	ml_srl_b32 v0, v69, 0x18
	ml_slb_store_b8  v0, v41, s19, #6, null
	ml_srl_b32 v0, v71, 0x8
	ml_slb_store_b8  v71, v41, s19, #128, null
	ml_slb_store_b8  v0, v41, s19, #130, null
	ml_srl_b32 v0, v71, 0x10
	ml_slb_store_b8  v0, v41, s19, #132, null
	ml_srl_b32 v0, v71, 0x18
	ml_slb_store_b8  v0, v41, s19, #134, null
	sl_wait lmcnt(0)
	sl_barrier 
	.loc	1 45 20                         ; candidate.py:45:20
	ml_slb_load_b32x1  v41, v40, s20, #0, null
	sl_add_i32 s21, s20, 0x400
	sl_add_i32 s23, s20, 0x800
	sl_add_i32 s25, s20, 0xc00
	ml_slb_load_b32x1  v43, v40, s21, #0, null
	.loc	1 46 25                         ; candidate.py:46:25
	sl_mov_b32 s34, 0x8400
	sl_mov_b32 s35, 0x504
	sl_mov_b32 s36, 0x60504
	.loc	1 45 20                         ; candidate.py:45:20
	ml_slb_load_b32x1  v45, v40, s23, #0, null
	.loc	1 46 25                         ; candidate.py:46:25
	sl_mov_b32 s37, 0x8800
	sl_mov_b32 s38, 0x8c00
	sl_mov_b32 s39, 0x9400
	.loc	1 45 20                         ; candidate.py:45:20
	ml_slb_load_b32x1  v47, v40, s25, #0, null
	.loc	1 46 25                         ; candidate.py:46:25
	sl_mov_b32 s40, 0x9800
	sl_mov_b32 s41, 0x9c00
	.loc	1 45 20                         ; candidate.py:45:20
	ml_slb_load_b32x1  v42, v39, s20, #0, null
	ml_slb_load_b32x1  v44, v39, s21, #0, null
	ml_slb_load_b32x1  v46, v39, s23, #0, null
	ml_slb_load_b32x1  v48, v39, s25, #0, null
	ml_slb_load_b32x1  v39, v38, s20, #0, null
	ml_slb_load_b32x1  v49, v38, s21, #0, null
	ml_slb_load_b32x1  v51, v38, s23, #0, null
	ml_slb_load_b32x1  v53, v38, s25, #0, null
	ml_slb_load_b32x1  v40, v37, s20, #0, null
	ml_slb_load_b32x1  v50, v37, s21, #0, null
	ml_slb_load_b32x1  v52, v37, s23, #0, null
	ml_slb_load_b32x1  v54, v37, s25, #0, null
	.loc	1 46 25                         ; candidate.py:46:25
	ml_slb_load_b8  v0, v36, s18, #256, null
	ml_slb_load_b8  v1, v36, s18, #257, null
	ml_slb_load_b8  v2, v36, s18, #288, null
	ml_slb_load_b8  v3, v36, s18, #289, null
	ml_slb_load_b8  v4, v35, s18, #0, null
	ml_slb_load_b8  v5, v35, s18, #1, null
	ml_slb_load_b8  v6, v35, s18, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v1, v0, 4
	ml_slb_load_b8  v7, v35, s18, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v2, v0, s35
	ml_slb_load_b8  v34, v36, s18, #768, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v38, v3, v0, s36
	ml_slb_load_b8  v55, v36, s18, #769, null
	ml_slb_load_b8  v56, v36, s18, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v4, v5, v4, 4
	ml_slb_load_b8  v57, v36, s18, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v4, v6, v4, s35
	ml_slb_load_b8  v58, v35, s18, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v7, v4, s36
	ml_slb_load_b8  v59, v35, s18, #513, null
	ml_slb_load_b8  v60, v35, s18, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v34, v55, v34, 4
	ml_slb_load_b8  v61, v35, s18, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v34, v56, v34, s35
	ml_slb_load_b8  v62, v36, s34, #256, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v56, v57, v34, s36
	ml_slb_load_b8  v63, v36, s34, #257, null
	ml_slb_load_b8  v64, v36, s34, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v55, v59, v58, 4
	ml_slb_load_b8  v65, v36, s34, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v55, v60, v55, s35
	ml_slb_load_b8  v66, v35, s34, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v55, v61, v55, s36
	ml_slb_load_b8  v67, v35, s34, #1, null
	ml_slb_load_b8  v68, v35, s34, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v57, v63, v62, 4
	ml_slb_load_b8  v69, v35, s34, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v57, v64, v57, s35
	ml_slb_load_b8  v70, v36, s34, #768, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v58, v65, v57, s36
	ml_slb_load_b8  v71, v36, s34, #769, null
	ml_slb_load_b8  v72, v36, s34, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v57, v67, v66, 4
	ml_slb_load_b8  v1, v36, s34, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v57, v68, v57, s35
	ml_slb_load_b8  v0, v35, s34, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v57, v69, v57, s36
	ml_slb_load_b8  v2, v35, s34, #513, null
	ml_slb_load_b8  v3, v35, s34, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v59, v71, v70, 4
	ml_slb_load_b8  v5, v35, s34, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v59, v72, v59, s35
	ml_slb_load_b8  v4, v36, s37, #256, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v60, v1, v59, s36
	ml_slb_load_b8  v6, v36, s37, #257, null
	ml_slb_load_b8  v7, v36, s37, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v2, v0, 4
	ml_slb_load_b8  v73, v36, s37, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v3, v0, s35
	ml_slb_load_b8  v34, v35, s37, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v59, v5, v0, s36
	ml_slb_load_b8  v74, v35, s37, #1, null
	ml_slb_load_b8  v75, v35, s37, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v4, v6, v4, 4
	ml_slb_load_b8  v76, v35, s37, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v4, v7, v4, s35
	ml_slb_load_b8  v77, v36, s37, #768, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v62, v73, v4, s36
	ml_slb_load_b8  v78, v36, s37, #769, null
	ml_slb_load_b8  v79, v36, s37, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v34, v74, v34, 4
	ml_slb_load_b8  v80, v36, s37, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v34, v75, v34, s35
	ml_slb_load_b8  v63, v35, s37, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v61, v76, v34, s36
	ml_slb_load_b8  v65, v35, s37, #513, null
	ml_slb_load_b8  v81, v35, s37, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v64, v78, v77, 4
	ml_slb_load_b8  v66, v35, s37, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v64, v79, v64, s35
	ml_slb_load_b8  v67, v36, s38, #256, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v64, v80, v64, s36
	ml_slb_load_b8  v68, v36, s38, #257, null
	ml_slb_load_b8  v69, v36, s38, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v63, v65, v63, 4
	ml_slb_load_b8  v82, v36, s38, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v63, v81, v63, s35
	ml_slb_load_b8  v1, v35, s38, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v63, v66, v63, s36
	ml_slb_load_b8  v70, v35, s38, #1, null
	ml_slb_load_b8  v71, v35, s38, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v65, v68, v67, 4
	ml_slb_load_b8  v72, v35, s38, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v65, v69, v65, s35
	ml_slb_load_b8  v0, v36, s38, #768, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v66, v82, v65, s36
	ml_slb_load_b8  v2, v36, s38, #769, null
	ml_slb_load_b8  v3, v36, s38, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v1, v70, v1, 4
	ml_slb_load_b8  v5, v36, s38, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v1, v71, v1, s35
	ml_slb_load_b8  v4, v35, s38, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v65, v72, v1, s36
	ml_slb_load_b8  v6, v35, s38, #513, null
	ml_slb_load_b8  v7, v35, s38, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v2, v0, 4
	ml_slb_load_b8  v73, v35, s38, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v3, v0, s35
	ml_slb_load_b8  v34, v36, s19, #256, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v68, v5, v0, s36
	ml_mov_b32 v5, 0x0
	ml_slb_load_b8  v74, v36, s19, #257, null
	ml_slb_load_b8  v75, v36, s19, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v6, v4, 4
	ml_mov_b32 v4, 0x0
	ml_mov_b32 v6, 0x0
	ml_slb_load_b8  v76, v36, s19, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v7, v0, s35
	ml_mov_b32 v7, 0x0
	ml_slb_load_b8  v77, v35, s19, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v67, v73, v0, s36
	ml_slb_load_b8  v78, v35, s19, #1, null
	ml_slb_load_b8  v79, v35, s19, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v74, v34, 4
	ml_mov_b32 v34, 0x0
	ml_slb_load_b8  v80, v35, s19, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v75, v0, s35
	ml_slb_load_b8  v81, v36, s19, #768, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v70, v76, v0, s36
	ml_slb_load_b8  v83, v36, s19, #769, null
	ml_slb_load_b8  v84, v36, s19, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v78, v77, 4
	ml_slb_load_b8  v85, v36, s19, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v0, v79, v0, s35
	ml_slb_load_b8  v82, v35, s19, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v69, v80, v0, s36
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[37:38], v[41:42], v[4:7]
	ml_slb_load_b8  v86, v35, s19, #513, null
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[69:70], v[41:42], v[4:7]
	ml_slb_load_b8  v87, v35, s19, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v83, v81, 4
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[55:56], v[39:40], v[0:3]
	ml_slb_load_b8  v88, v35, s19, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v84, v37, s35
	sl_wait lmcnt(4)
	ml_byte_permute_b32 v38, v85, v37, s36
	ml_slb_load_b8  v71, v36, s39, #256, null
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[57:58], v[43:44], v[0:3]
	ml_slb_load_b8  v72, v36, s39, #257, null
	sl_wait lmcnt(4)
	ml_byte_permute_b32 v37, v86, v82, 4
	ml_slb_load_b8  v89, v36, s39, #288, null
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[59:60], v[49:50], v[0:3]
	ml_slb_load_b8  v90, v36, s39, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v87, v37, s35
	ml_slb_load_b8  v91, v35, s39, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v88, v37, s36
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[61:62], v[45:46], v[0:3]
	ml_slb_load_b8  v92, v35, s39, #1, null
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[37:38], v[39:40], v[4:7]
	ml_slb_load_b8  v93, v35, s39, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v72, v71, 4
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[63:64], v[51:52], v[0:3]
	ml_slb_load_b8  v94, v35, s39, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v89, v37, s35
	ml_slb_load_b8  v73, v36, s39, #768, null
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[65:66], v[47:48], v[0:3]
	ml_slb_load_b8  v95, v36, s39, #769, null
	sl_wait lmcnt(4)
	ml_byte_permute_b32 v38, v92, v91, 4
	ml_slb_load_b8  v96, v36, s39, #800, null
	ml_matrix_mad_i32_i8_m16n16k32 v[0:3], v[67:68], v[53:54], v[0:3]
	ml_slb_load_b8  v97, v36, s39, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v58, v93, v38, s35
	ml_byte_permute_b32 v38, v90, v37, s36
	ml_slb_load_b8  v74, v35, s39, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v94, v58, s36
	ml_slb_load_b8  v75, v35, s39, #513, null
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[37:38], v[43:44], v[4:7]
	ml_slb_load_b8  v76, v35, s39, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v95, v73, 4
	ml_slb_load_b8  v77, v35, s39, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v96, v37, s35
	ml_slb_load_b8  v78, v36, s40, #256, null
	ml_slb_load_b8  v79, v36, s40, #257, null
	ml_slb_load_b8  v80, v36, s40, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v38, v75, v74, 4
	ml_slb_load_b8  v98, v36, s40, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v60, v76, v38, s35
	ml_byte_permute_b32 v38, v97, v37, s36
	ml_slb_load_b8  v81, v35, s40, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v77, v60, s36
	ml_slb_load_b8  v41, v35, s40, #1, null
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[37:38], v[49:50], v[4:7]
	ml_slb_load_b8  v42, v35, s40, #32, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v79, v78, 4
	ml_slb_load_b8  v55, v35, s40, #33, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v80, v37, s35
	ml_slb_load_b8  v56, v36, s40, #768, null
	ml_slb_load_b8  v39, v36, s40, #769, null
	ml_slb_load_b8  v40, v36, s40, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v38, v41, v81, 4
	ml_slb_load_b8  v57, v36, s40, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v42, v42, v38, s35
	ml_byte_permute_b32 v38, v98, v37, s36
	ml_slb_load_b8  v58, v35, s40, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v55, v42, s36
	ml_slb_load_b8  v43, v35, s40, #513, null
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[37:38], v[45:46], v[4:7]
	ml_slb_load_b8  v44, v35, s40, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v39, v56, 4
	ml_slb_load_b8  v59, v35, s40, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v40, v37, s35
	ml_slb_load_b8  v69, v36, s41, #256, null
	ml_slb_load_b8  v60, v36, s41, #257, null
	ml_slb_load_b8  v49, v36, s41, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v38, v43, v58, 4
	ml_slb_load_b8  v50, v36, s41, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v40, v44, v38, s35
	ml_byte_permute_b32 v38, v57, v37, s36
	ml_slb_load_b8  v41, v35, s41, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v59, v40, s36
	ml_slb_load_b8  v42, v35, s41, #1, null
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[37:38], v[51:52], v[4:7]
	ml_slb_load_b8  v45, v35, s41, #32, null
	ml_slb_load_b8  v46, v35, s41, #33, null
	ml_slb_load_b8  v39, v36, s41, #768, null
	ml_slb_load_b8  v43, v36, s41, #769, null
	ml_slb_load_b8  v40, v36, s41, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v37, v42, v41, 4
	ml_slb_load_b8  v38, v36, s41, #801, null
	ml_byte_permute_b32 v36, v60, v69, 4
	ml_byte_permute_b32 v36, v49, v36, s35
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v42, v45, v37, s35
	ml_slb_load_b8  v44, v35, s41, #512, null
	ml_byte_permute_b32 v37, v50, v36, s36
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v36, v46, v42, s36
	ml_slb_load_b8  v41, v35, s41, #513, null
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[36:37], v[47:48], v[4:7]
	ml_slb_load_b8  v42, v35, s41, #544, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v36, v43, v39, 4
	ml_slb_load_b8  v35, v35, s41, #545, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v36, v40, v36, s35
	sl_wait lmcnt(4)
	ml_byte_permute_b32 v36, v38, v36, s36
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v37, v41, v44, 4
	sl_wait lmcnt(1)
	ml_byte_permute_b32 v37, v42, v37, s35
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v35, v35, v37, s36
	ml_matrix_mad_i32_i8_m16n16k32 v[4:7], v[35:36], v[53:54], v[4:7]
	ml_mov_b32 v35, 0x0
	.loc	1 47 21                         ; candidate.py:47:21
	sl_and_savetmsk_b64 {s[18:19], wcr}, s[16:17], tmsk
	; mask branch BB0_51
BB0_50:
	.loc	1 0 21 is_stmt 0                ; candidate.py:0:21
	sl_mov_b32 s16, 0x5c
	ml_addo_u32 {v32, tcr}, s16, v32
	ml_addc_i32 v33, 0, v33, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v35, v[32:33], kop=0
BB0_51:
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[18:19]
	.loc	1 47 21                         ; candidate.py:47:21
	sl_and_savetmsk_b64 {s[16:17], wcr}, s[14:15], tmsk
	; mask branch BB0_53
BB0_52:
	.loc	1 47 39                         ; candidate.py:47:39
	sl_mov_b32 s14, 0x5c
	ml_addo_u32 {v30, tcr}, s14, v30
	ml_addc_i32 v31, 0, v31, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v34, v[30:31], kop=0
BB0_53:
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[16:17]
	.loc	1 47 21                         ; candidate.py:47:21
	ml_mov_b32 v31, 0x0
	ml_mov_b32 v30, 0x0
	sl_and_savetmsk_b64 {s[14:15], wcr}, s[12:13], tmsk
	; mask branch BB0_55
BB0_54:
	.loc	1 47 39                         ; candidate.py:47:39
	sl_mov_b32 s12, 0x5c
	ml_addo_u32 {v28, tcr}, s12, v28
	ml_addc_i32 v29, 0, v29, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v30, v[28:29], kop=0
BB0_55:
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[14:15]
	.loc	1 47 21                         ; candidate.py:47:21
	sl_and_savetmsk_b64 {s[12:13], wcr}, s[10:11], tmsk
	; mask branch BB0_57
BB0_56:
	.loc	1 47 39                         ; candidate.py:47:39
	sl_mov_b32 s10, 0x5c
	ml_addo_u32 {v26, tcr}, s10, v26
	ml_addc_i32 v27, 0, v27, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v31, v[26:27], kop=0
BB0_57:
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[12:13]
	.loc	1 47 21                         ; candidate.py:47:21
	ml_mov_b32 v27, 0x0
	ml_mov_b32 v26, 0x0
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[6:7], tmsk
	; mask branch BB0_59
BB0_58:
	.loc	1 47 39                         ; candidate.py:47:39
	sl_mov_b32 s6, 0x5c
	ml_addo_u32 {v24, tcr}, s6, v24
	ml_addc_i32 v25, 0, v25, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v26, v[24:25], kop=0
BB0_59:
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 47 21                         ; candidate.py:47:21
	sl_and_savetmsk_b64 {s[6:7], wcr}, s[4:5], tmsk
	; mask branch BB0_61
BB0_60:
	.loc	1 47 39                         ; candidate.py:47:39
	sl_mov_b32 s4, 0x5c
	ml_addo_u32 {v22, tcr}, s4, v22
	ml_addc_i32 v23, 0, v23, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v27, v[22:23], kop=0
BB0_61:
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[6:7]
	.loc	1 47 21                         ; candidate.py:47:21
	ml_mov_b32 v23, 0x0
	ml_mov_b32 v22, 0x0
	sl_and_savetmsk_b64 {s[4:5], wcr}, s[2:3], tmsk
	; mask branch BB0_63
BB0_62:
	.loc	1 47 39                         ; candidate.py:47:39
	sl_mov_b32 s2, 0x5c
	ml_addo_u32 {v20, tcr}, s2, v20
	ml_addc_i32 v21, 0, v21, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v22, v[20:21], kop=0
BB0_63:
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[4:5]
	.loc	1 47 21                         ; candidate.py:47:21
	sl_and_savetmsk_b64 {s[2:3], wcr}, s[0:1], tmsk
	; mask branch BB0_65
BB0_64:
	.loc	1 47 39                         ; candidate.py:47:39
	sl_mov_b32 s0, 0x5c
	ml_addo_u32 {v18, tcr}, s0, v18
	ml_addc_i32 v19, 0, v19, tcr
	.loc	1 47 21                         ; candidate.py:47:21
	ml_lsa_load_a64_dword  v23, v[18:19], kop=0
BB0_65:                                 ; %.peel.next
	.loc	1 0 21                          ; candidate.py:0:21
	sl_or_b64 {tmsk, wcr}, tmsk, s[2:3]
	sl_mov_b32 s15, 0xffffffff
	.loc	1 41 23 is_stmt 1               ; candidate.py:41:23
	sl_add_i32 s2, s31, 0x1
	.loc	1 45 41                         ; candidate.py:45:41
	sl_add_i64 s[0:1], s[32:33], 0x1800
	.loc	1 45 20 is_stmt 0               ; candidate.py:45:20
	sl_mull_u32 s3, s2, 0x4000
	.loc	1 41 23 is_stmt 1               ; candidate.py:41:23
	sl_cmp_lt_i32 wcr, s2, 0x2
	sl_csel_b32 s4, s3, 0x0, wcr
	sl_mov_b32 s3, 0x1800
	.loc	1 45 20                         ; candidate.py:45:20
	sl_mov_b32 s2, s15
	sl_add_i32 s25, s4, s30
	sl_sme_load_16x1b64_col s[0:3], s[24:25], 0x0, 0x0, 0x0, 0x1
	sl_mov_b32 s73, s25
	sl_sme_load_16x1b64_col s[0:3], s[72:73], 0x0, 0x0, 0x800, 0x1
	sl_sme_load_16x1b64_col s[0:3], s[24:25], 0x0, 0x2, 0x200, 0x1
	sl_sme_load_16x1b64_col s[0:3], s[72:73], 0x0, 0x2, 0xa00, 0x1
	ml_mov_b32 v18, 0x60
	.loc	1 48 21                         ; candidate.py:48:21
	ml_mad_u32_u16 v10, v10, v18, 0
	sl_mov_b64 s[12:13], s[26:27]
	ml_lsa_load_dword v10, s[12:15], signed v10, noreg, #92, ca
	.loc	1 50 28                         ; candidate.py:50:28
	ml_cvt_f32_i32  v7, v7
	ml_cvt_f32_i32  v6, v6
	ml_cvt_f32_i32  v5, v5
	ml_cvt_f32_i32  v4, v4
	ml_cvt_f32_i32  v3, v3
	ml_cvt_f32_i32  v2, v2
	ml_cvt_f32_i32  v1, v1
	ml_cvt_f32_i32  v0, v0
	.loc	1 38 44                         ; candidate.py:38:44
	ml_shl_b32 v8, v8, 0x1
	.loc	1 41 23                         ; candidate.py:41:23
	sl_wait vmcnt(0) g2scnt(0)
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v18, v23, v10
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v7, v18, v7, v17
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v17, v22, v10
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v6, v17, v6, v16
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v16, v27, v10
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v5, v16, v5, v15
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v15, v26, v10
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v4, v15, v4, v14
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v14, v31, v10
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v3, v14, v3, v13
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v13, v30, v10
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v2, v13, v2, v12
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v12, v34, v10
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v1, v12, v1, v11
	.loc	1 49 30                         ; candidate.py:49:30
	ml_mul_f32 v10, v35, v10
	.loc	1 50 20                         ; candidate.py:50:20
	ml_fma_f32 v0, v10, v0, v9
	.loc	1 38 44                         ; candidate.py:38:44
	ml_and_b32 v9, v8, 0xe
	.loc	1 38 31 is_stmt 0               ; candidate.py:38:31
	ml_add_i32 v9, s22, v9
	.loc	1 37 45 is_stmt 1               ; candidate.py:37:45
	ml_and_b32 v10, tid, 0x38
	ml_srl_b32 v10, v10, 0x3
	.loc	1 37 32 is_stmt 0               ; candidate.py:37:32
	ml_add_i32 v10, s74, v10
	ml_add_i32 v11, v10, 0x18
	ml_add_i32 v12, v10, 0x10
	ml_add_i32 v13, v10, 0x8
	.loc	1 41 23 is_stmt 1               ; candidate.py:41:23
	sl_barrier 
	.loc	1 52 31                         ; candidate.py:52:31
	ml_cmp_lt_u32 tcr, v10, 0x7ee
	.loc	1 51 30                         ; candidate.py:51:30
	ml_shl_b32 v14, v10, 0xb
	.loc	1 51 17 is_stmt 0               ; candidate.py:51:17
	ml_sra_b32 v15, v14, 0x1f
	ml_shl_b32 v10, v10, 0xc
	.loc	1 52 31 is_stmt 1               ; candidate.py:52:31
	sl_mov_b64 s[6:7], tcr
	ml_cmp_lt_u32 tcr, v13, 0x7ee
	.loc	1 51 17                         ; candidate.py:51:17
	ml_shl_b32 v15, v15, 0x1
	ml_srl_b32 v16, v14, 0x1f
	ml_or_b32 v15, v15, v16
	.loc	1 52 31                         ; candidate.py:52:31
	sl_mov_b64 s[4:5], tcr
	ml_cmp_lt_u32 tcr, v12, 0x7ee
	.loc	1 51 17                         ; candidate.py:51:17
	ml_mov_b32 v16, s29
	ml_shl_b32 v13, v13, 0xc
	ml_shl_b32 v12, v12, 0xc
	.loc	1 52 31                         ; candidate.py:52:31
	sl_mov_b64 s[0:1], tcr
	ml_cmp_lt_u32 tcr, v11, 0x7ee
	.loc	1 51 17                         ; candidate.py:51:17
	ml_shl_b32 v11, v11, 0xc
	.loc	1 51 53 is_stmt 0               ; candidate.py:51:53
	ml_cvt_bf16_f32  v0, v0
	ml_cvt_bf16_f32  v1, v1
	.loc	1 52 31 is_stmt 1               ; candidate.py:52:31
	sl_mov_b64 s[2:3], tcr
	.loc	1 51 17                         ; candidate.py:51:17
	ml_addo_u32 {v10, tcr}, s28, v10
	.loc	1 51 53 is_stmt 0               ; candidate.py:51:53
	ml_cvt_bf16_f32  v2, v2
	ml_cvt_bf16_f32  v3, v3
	ml_cvt_bf16_f32  v4, v4
	.loc	1 51 17                         ; candidate.py:51:17
	ml_addc_i32 v15, v16, v15, tcr
	.loc	1 51 34                         ; candidate.py:51:34
	ml_shl_b32 v16, v9, 0x1
	ml_addo_u32 {v10, tcr}, v16, v10
	ml_or_b32 v9, v14, v9
	ml_shl_b32 v9, v9, 0x1
	ml_or_b32 v13, v13, v16
	ml_addc_i32 v14, 0, v15, tcr
	ml_or_b32 v12, v12, v16
	ml_or_b32 v11, v11, v16
	.loc	1 51 53                         ; candidate.py:51:53
	ml_cvt_bf16_f32  v5, v5
	ml_cvt_bf16_f32  v6, v6
	ml_cvt_bf16_f32  v7, v7
	sl_mov_b32 s10, 0x1000504
	ml_byte_permute_b32 v0, v1, v0, s10
	ml_byte_permute_b32 v1, v3, v2, s10
	ml_byte_permute_b32 v2, v5, v4, s10
	ml_byte_permute_b32 v3, v7, v6, s10
	ml_and_b32 v4, tid, 0x1
	ml_cmp_eq_u32 tcr, v4, 0x0
	ml_mov_b32 v4, 0x7632
	ml_mov_b32 v5, 0x5410
	ml_csel_b32 v6, v5, v4, tcr
	ml_csel_b32 v7, v4, v5, tcr
	sl_mov_b32 s10, 0x2010200
	ml_byte_permute_b32 v6, v6, v6, s10
	ml_pk_shl_b16 v6, v6, 0x40004
	ml_pk_srl_b8 v6, v6, 0x40004
	ml_byte_permute_b32 v15, v0, v1, v6
	ml_byte_permute_b32 v7, v7, v7, s10
	ml_pk_shl_b16 v7, v7, 0x40004
	ml_pk_srl_b8 v7, v7, 0x40004
	ml_byte_permute_b32 v0, v0, v1, v7
	ml_bfe2_b32 v1, tid, 0x25
	ml_anyop3_b32 v1, 62, v8, v1, 0xfffffff8
	ml_slb_shuffle_rtn_b32 v8, v15, v1
	ml_byte_permute_b32 v6, v2, v3, v6
	ml_byte_permute_b32 v2, v2, v3, v7
	ml_xor_b32 v3, v1, 0x1
	ml_slb_shuffle_rtn_b32 v0, v0, v3
	ml_and_b32 v7, tid, 0x20
	ml_cmp_eq_u32 tcr, v7, 0x0
	ml_mov_b32 v7, 0x1054
	ml_slb_shuffle_rtn_b32 v1, v6, v1
	ml_csel_b32 v5, v5, v7, tcr
	ml_mov_b32 v6, 0x3276
	ml_csel_b32 v4, v4, v6, tcr
	ml_slb_shuffle_rtn_b32 v2, v2, v3
	ml_byte_permute_b32 v3, v5, v5, s10
	ml_pk_shl_b16 v3, v3, 0x40004
	ml_pk_srl_b8 v3, v3, 0x40004
	ml_byte_permute_b32 v4, v4, v4, s10
	ml_pk_shl_b16 v4, v4, 0x40004
	.loc	1 51 46                         ; candidate.py:51:46
	ml_mov_v2s_b32 s12, v10, 0x0
	.loc	1 51 53                         ; candidate.py:51:53
	ml_pk_srl_b8 v4, v4, 0x40004
	.loc	1 51 46                         ; candidate.py:51:46
	ml_mov_v2s_b32 s13, v14, 0x0
	ml_mov_b32 v6, s12
	ml_sub_i32 v6, v10, v6
	.loc	1 51 53                         ; candidate.py:51:53
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v5, v8, v0, v3
	ml_byte_permute_b32 v0, v8, v0, v4
	.loc	1 51 46                         ; candidate.py:51:46
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v5, s[12:15], signed v6, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	ml_sub_i32 v5, v13, v9
	ml_mov_v2s_b32 s6, v5, 0x0
	ml_sub_i32 v5, v12, v9
	ml_mov_v2s_b32 s7, v5, 0x0
	.loc	1 51 53                         ; candidate.py:51:53
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v3, v1, v2, v3
	.loc	1 51 46                         ; candidate.py:51:46
	ml_add_i32 v5, s6, v6
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v0, s[12:15], signed v5, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	ml_add_i32 v0, s7, v6
	ml_sub_i32 v5, v11, v9
	ml_mov_v2s_b32 s4, v5, 0x0
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v3, s[12:15], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 51 53                         ; candidate.py:51:53
	ml_byte_permute_b32 v0, v1, v2, v4
	.loc	1 51 46                         ; candidate.py:51:46
	ml_add_i32 v1, s4, v6
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[2:3], tmsk
	ml_lsa_store_dword v0, s[12:15], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 51 4                          ; candidate.py:51:4
	sl_eop 
.Ltmp1:
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	down_group256.kd
	.type	down_group256.kd,@object
	.size	down_group256.kd, 64
down_group256.kd:
	.asciz	"\000\000\000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	down_group256@rel64-down_group256.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	537306
	.asciz	"\003\000\224\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	down_group256, .Lfunc_end0-down_group256
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 12440
; NumSgprs: 96
; NumVgprs: 107
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 11
; VGPRBlocks: 26
; NumSGPRsForWarpsPerNU: 92
; NumVGPRsForWarpsPerNR: 107
; ReqNTIDx: 0
; MaxNTIDx: 0
; MinCTASm: 0
; ActiveWarp: 2
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
	.long	155                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0x94 DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"candidate.py"                  ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/workspace/experiments/minicpm-s2/framework/20261026T062610126686Z-biv150-down-group256-component/source" ; DW_AT_comp_dir
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
    .group_segment_fixed_size: 0
    .kernarg_segment_align: 8
    .kernarg_segment_size: 56
    .max_flat_workgroup_size: 0
    .name:           down_group256
    .private_segment_fixed_size: 0
    .sgpr_count:     96
    .sgpr_spill_count: 0
    .symbol:         down_group256.kd
    .vgpr_count:     107
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
