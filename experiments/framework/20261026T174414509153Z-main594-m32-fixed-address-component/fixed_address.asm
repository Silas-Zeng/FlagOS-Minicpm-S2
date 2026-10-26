	.text
	.globl	fixed_address_mm                ; -- Begin function fixed_address_mm
	.p2align	3
	.type	fixed_address_mm,@function
	.iluvatar_kernel fixed_address_mm
fixed_address_mm:                       ; @fixed_address_mm
.Lfunc_begin0:
	.file	1 "/workspace/experiments/minicpm-s2/framework/20261026T174414509153Z-main594-m32-fixed-address-component/source" "candidate.py"
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
		warp_sgpr_count = 38
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
	sl_mov_b32 s30, tcr_lo
	ml_vrf_init_u32 v4, tcr
.Ltmp0:
	.loc	1 10 22 prologue_end            ; candidate.py:10:22
	sl_lsa_load_b32x16 s[12:27], s[4:5], noreg, #0, ca
	.loc	1 16 33                         ; candidate.py:16:33
	sl_srl_b32 {s33, wcr}, tcr_lo, 0x6
	.loc	1 22 31                         ; candidate.py:22:31
	sl_mov_b32 s5, 0x0
	.loc	1 27 18                         ; candidate.py:27:18
	sl_bfe2_b32 s2, tcr_lo, 0x26
	sl_wait smcnt(0)
	sl_mov_b32 s26, 0xffffffff
	.loc	1 16 13                         ; candidate.py:16:13
	sl_and_b32 {s31, wcr}, s6, 0x7fffffe0
	.loc	1 22 31                         ; candidate.py:22:31
	sl_mull_u32 s4, s7, 0x100
	.loc	1 27 18                         ; candidate.py:27:18
	sl_bfe2_b32 s3, s33, 0x41
	sl_mull_u32 s7, s3, 0x400
	.loc	1 24 17                         ; candidate.py:24:17
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v2, 0x0
	.loc	1 22 21                         ; candidate.py:22:21
	sl_mull_u32 s0, s21, s31
	.loc	1 27 18                         ; candidate.py:27:18
	sl_mull_u32 s27, s21, 0x2
	.loc	1 22 9                          ; candidate.py:22:9
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[28:29], wcr}, s[0:1], 0x1
	sl_add_i64 s[0:1], s[12:13], s[28:29]
	.loc	1 22 31 is_stmt 0               ; candidate.py:22:31
	sl_add_i64 s[24:25], s[0:1], s[4:5]
	.loc	1 27 18 is_stmt 1               ; candidate.py:27:18
	sl_mull_u32 s0, s2, 0x1000
	sl_add_i32 s32, s7, s0
	sl_add_i32 s9, s32, 0x8000
	sl_mull_u32 s0, s3, 0x40
	sl_mull_u32 s1, s2, s21
	sl_mull_u32 s1, s1, 0x20
	sl_add_i32 s8, s1, s0
	sl_sme_load_16x1b64_rowxfb16 s[24:27], s[8:9], 0x0, 0x0, 0x0, 0x1
	.loc	1 17 13                         ; candidate.py:17:13
	sl_mull_u32 s0, s6, 0x40
	sl_and_b32 {s21, wcr}, s0, 0x7c0
	.loc	1 23 9                          ; candidate.py:23:9
	sl_add_i64 s[0:1], s[14:15], s[4:5]
	.loc	1 23 32 is_stmt 0               ; candidate.py:23:32
	sl_mull_u32 s2, s22, s21
	.loc	1 23 20                         ; candidate.py:23:20
	sl_sra_b32 {s3, wcr}, s2, 0x1f
	sl_shl_b64 {s[2:3], wcr}, s[2:3], 0x1
	sl_add_i64 s[0:1], s[0:1], s[2:3]
	.loc	1 27 32 is_stmt 1               ; candidate.py:27:32
	sl_bfe2_b32 s6, tcr_lo, 0x46
	sl_bfe2_b32 s7, s33, 0x22
	sl_mull_u32 s3, s22, 0x2
	sl_mov_b32 s2, s26
	sl_mull_u32 s9, s7, 0x800
	sl_mull_u32 s14, s6, 0x200
	sl_add_i32 s9, s9, s14
	sl_mull_u32 s33, s9, 0x2
	sl_mull_u32 s6, s6, 0x40
	sl_mull_u32 s7, s7, s22
	sl_mull_u32 s7, s7, 0x20
	sl_add_i32 s6, s7, s6
	sl_mov_b32 s7, s33
	sl_sme_load_16x1b64_col s[0:3], s[6:7], 0x0, 0x0, 0x0, 0x1
	sl_mull_u32 s7, s22, 0x40
	sl_add_i32 s14, s6, s7
	sl_mov_b32 s15, s33
	sl_sme_load_16x1b64_col s[0:3], s[14:15], 0x0, 0x0, 0x800, 0x1
	.loc	1 16 33                         ; candidate.py:16:33
	sl_and_b32 {s22, wcr}, tcr_lo, 0x100
.Ltmp1:
	.file	2 "/usr/local/lib/python3.12/site-packages/triton/language" "standard.py"
	.loc	2 65 17                         ; standard.py:65:17 @[ candidate.py:26:31 ]
	sl_add_i32 s2, s20, 0x7f
.Ltmp2:
	.loc	1 26 21                         ; candidate.py:26:21
	sl_cmp_gt_i32 wcr, s2, 0x7f
	ml_mov_b32 v3, 0x0
	sl_cbr_wcrz BB0_4, wcr
; %bb.1:                                ; %.lr.ph
.Ltmp3:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:26:31 ]
	sl_sra_b32 {s7, wcr}, s2, 0x1f
	sl_srl_b32 {s7, wcr}, s7, 0x19
	sl_add_i32 s2, s2, s7
	sl_sra_b32 {s20, wcr}, s2, 0x7
	ml_shl_b32 v0, v4, 0x2
	ml_and_b32 v0, v0, 0xfc
	sl_mull_u32 s2, s22, 0x10
	ml_add_i32 v5, s2, v0
	ml_shl_b32 v1, v4, 0x6
	sl_mov_b32 s2, 0x3300
	ml_anyop3_b32 v6, s2, v1, v0, 0xfffffff8
	ml_xor_b32 v7, v6, 0x10
	ml_xor_b32 v8, v6, 0x20
	ml_xor_b32 v9, v6, 0x30
.Ltmp4:
	.loc	1 26 21                         ; candidate.py:26:21
	sl_add_i64 s[0:1], s[0:1], 0x100
	sl_add_i64 s[12:13], s[12:13], s[4:5]
	sl_add_i64 s[12:13], s[12:13], s[28:29]
	sl_add_i64 s[24:25], s[12:13], 0x100
	ml_mov_b32 v0, 0x0
	ml_xor_b32 v10, v5, 0x80
	sl_mov_b32 s4, s26
	ml_mov_b32 v1, 0x0
BB0_2:                                  ; =>This Inner Loop Header: Depth=1
	sl_add_i32 s2, s4, 0x1
	sl_cmp_lt_i32 wcr, s2, 0x2
	sl_csel_b32 s4, s2, 0x0, wcr
	.loc	1 27 18                         ; candidate.py:27:18
	sl_wait g2scnt(0)
	sl_barrier_req 0x0
	sl_barrier_wait 0x0
	sl_mull_u32 s28, s4, 0x2000
	sl_add_i32 s12, s28, 0x8000
	ml_slb_load_b32x1  v11, v5, s12, #0, null
	sl_add_i32 s13, s28, 0x8400
	.loc	1 26 21                         ; candidate.py:26:21
	sl_add_i32 s2, s5, 0x1
	sl_cmp_lt_i32 wcr, s2, 0x2
	.loc	1 27 18                         ; candidate.py:27:18
	ml_slb_load_b32x1  v12, v5, s12, #256, null
	.loc	1 26 21                         ; candidate.py:26:21
	sl_csel_b32 s5, s2, 0x0, wcr
	.loc	1 27 18                         ; candidate.py:27:18
	sl_mull_u32 s2, s5, 0x2000
	sl_add_i32 s2, s32, s2
	ml_slb_load_b32x1  v13, v5, s13, #0, null
	sl_add_i32 s9, s2, 0x8000
	sl_sme_load_16x1b64_rowxfb16 s[24:27], s[8:9], 0x0, 0x0, 0x0, 0x1
	sl_add_i32 s9, s28, 0x8800
	ml_slb_load_b32x1  v14, v5, s13, #256, null
	.loc	1 27 32 is_stmt 0               ; candidate.py:27:32
	sl_mull_u32 s7, s5, 0x4000
	sl_mov_b32 s2, s26
	sl_add_i32 s7, s7, s33
	.loc	1 27 18                         ; candidate.py:27:18
	ml_slb_load_b32x1  v15, v5, s9, #0, null
	.loc	1 27 32                         ; candidate.py:27:32
	sl_sme_load_16x1b64_col s[0:3], s[6:7], 0x0, 0x0, 0x0, 0x1
	sl_mov_b32 s15, s7
	sl_sme_load_16x1b64_col s[0:3], s[14:15], 0x0, 0x0, 0x800, 0x1
	.loc	1 27 18                         ; candidate.py:27:18
	ml_slb_load_b32x1  v16, v5, s9, #256, null
	sl_add_i32 s2, s28, 0x8c00
	.loc	1 27 32                         ; candidate.py:27:32
	sl_add_i32 s7, s28, s28
	sl_add_i32 s15, s7, 0x400
	.loc	1 27 18                         ; candidate.py:27:18
	ml_slb_load_b32x1  v17, v5, s2, #0, null
	.loc	1 27 32                         ; candidate.py:27:32
	sl_add_i32 s28, s7, 0x800
	sl_add_i32 s29, s7, 0xc00
	.loc	1 26 21 is_stmt 1               ; candidate.py:26:21
	sl_add_i64 s[0:1], s[0:1], 0x100
	.loc	1 27 18                         ; candidate.py:27:18
	ml_slb_load_b32x1  v18, v5, s2, #256, null
	.loc	1 26 21                         ; candidate.py:26:21
	sl_add_i32 s20, s20, 0xffffffff
	sl_cmp_eq_u32 wcr, s20, 0x0
	sl_add_i64 s[24:25], s[24:25], 0x100
	.loc	1 27 18                         ; candidate.py:27:18
	ml_slb_load_b32x1  v19, v10, s12, #512, null
	.loc	1 27 32 is_stmt 0               ; candidate.py:27:32
	ml_slb_load_b32x1  v21, v6, s7, #0, null
	ml_slb_load_b32x1  v22, v7, s7, #0, null
	.loc	1 27 18                         ; candidate.py:27:18
	ml_slb_load_b32x1  v20, v10, s12, #768, null
	.loc	1 27 32                         ; candidate.py:27:32
	ml_slb_load_b32x1  v23, v8, s7, #0, null
	ml_slb_load_b32x1  v24, v9, s7, #0, null
	.loc	1 29 23 is_stmt 1               ; candidate.py:29:23
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[11:12], v[21:22], v[0:3]
	.loc	1 27 18                         ; candidate.py:27:18
	ml_slb_load_b32x1  v11, v10, s13, #512, null
	.loc	1 27 32 is_stmt 0               ; candidate.py:27:32
	ml_slb_load_b32x1  v21, v6, s15, #0, null
	ml_slb_load_b32x1  v22, v7, s15, #0, null
	.loc	1 29 23 is_stmt 1               ; candidate.py:29:23
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[19:20], v[23:24], v[0:3]
	.loc	1 27 18                         ; candidate.py:27:18
	ml_slb_load_b32x1  v12, v10, s13, #768, null
	.loc	1 27 32 is_stmt 0               ; candidate.py:27:32
	ml_slb_load_b32x1  v19, v8, s15, #0, null
	ml_slb_load_b32x1  v20, v9, s15, #0, null
	.loc	1 29 23 is_stmt 1               ; candidate.py:29:23
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[13:14], v[21:22], v[0:3]
	.loc	1 27 18                         ; candidate.py:27:18
	ml_slb_load_b32x1  v13, v10, s9, #512, null
	.loc	1 27 32 is_stmt 0               ; candidate.py:27:32
	ml_slb_load_b32x1  v21, v6, s28, #0, null
	ml_slb_load_b32x1  v22, v7, s28, #0, null
	.loc	1 29 23 is_stmt 1               ; candidate.py:29:23
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[11:12], v[19:20], v[0:3]
	.loc	1 27 18                         ; candidate.py:27:18
	ml_slb_load_b32x1  v14, v10, s9, #768, null
	.loc	1 27 32 is_stmt 0               ; candidate.py:27:32
	ml_slb_load_b32x1  v11, v8, s28, #0, null
	ml_slb_load_b32x1  v12, v9, s28, #0, null
	ml_slb_load_b32x1  v19, v6, s29, #0, null
	.loc	1 29 23 is_stmt 1               ; candidate.py:29:23
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[15:16], v[21:22], v[0:3]
	.loc	1 27 18                         ; candidate.py:27:18
	ml_slb_load_b32x1  v15, v10, s2, #512, null
	.loc	1 27 32 is_stmt 0               ; candidate.py:27:32
	ml_slb_load_b32x1  v20, v7, s29, #0, null
	.loc	1 27 18                         ; candidate.py:27:18
	ml_slb_load_b32x1  v16, v10, s2, #768, null
	.loc	1 29 23 is_stmt 1               ; candidate.py:29:23
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[13:14], v[11:12], v[0:3]
	.loc	1 27 32                         ; candidate.py:27:32
	ml_slb_load_b32x1  v11, v8, s29, #0, null
	ml_slb_load_b32x1  v12, v9, s29, #0, null
	.loc	1 29 23                         ; candidate.py:29:23
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[17:18], v[19:20], v[0:3]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[15:16], v[11:12], v[0:3]
	.loc	1 26 21                         ; candidate.py:26:21
	sl_cbr_wcrz BB0_2, wcr
; %bb.3:                                ; %._crit_edge.loopexit
	.loc	1 35 54                         ; candidate.py:35:54
	ml_cvt_bf16_f32  v0, v0
	ml_cvt_bf16_f32  v1, v1
	ml_cvt_bf16_f32  v2, v2
	ml_cvt_bf16_f32  v3, v3
BB0_4:                                  ; %._crit_edge
	.loc	1 17 33                         ; candidate.py:17:33
	ml_shl_b32 v7, v4, 0x1
	ml_and_b32 v8, v7, 0xe
	sl_srl_b32 {s0, wcr}, s30, 0x2
	sl_and_b32 {s0, wcr}, s0, 0x30
	.loc	1 16 33                         ; candidate.py:16:33
	sl_srl_b32 {s1, wcr}, s22, 0x4
	ml_bfe2_b32 v4, v4, 0x63
	.loc	1 26 21                         ; candidate.py:26:21
	sl_wait g2scnt(0)
	sl_barrier 
	.loc	1 32 21                         ; candidate.py:32:21
	sl_add_i32 s1, s31, s1
	ml_add_i32 v9, s1, v4
	ml_add_i32 v10, v9, 0x8
	.loc	1 35 26                         ; candidate.py:35:26
	ml_mul_u64_u32 v[4:5], s23, v9
	.loc	1 35 15 is_stmt 0               ; candidate.py:35:15
	sl_mull_u32 s1, s23, 0x2
	.loc	1 33 21 is_stmt 1               ; candidate.py:33:21
	sl_add_i32 s0, s21, s0
	.loc	1 35 15                         ; candidate.py:35:15
	ml_mul_u64_u32 v[5:6], s1, v10
	.loc	1 33 21                         ; candidate.py:33:21
	ml_add_i32 v6, s0, v8
	.loc	1 34 21                         ; candidate.py:34:21
	ml_cmp_gt_i32 tcr, s18, v9
	.loc	1 35 15                         ; candidate.py:35:15
	ml_sra_b32 v8, v4, 0x1f
	ml_shl_b32 v9, v4, 0x1
	ml_shl_b32 v8, v8, 0x1
	.loc	1 34 21                         ; candidate.py:34:21
	sl_mov_b64 s[0:1], tcr
	ml_cmp_gt_i32 tcr, s18, v10
	.loc	1 35 15                         ; candidate.py:35:15
	ml_srl_b32 v10, v4, 0x1f
	ml_or_b32 v8, v8, v10
	ml_mov_b32 v10, s17
	.loc	1 34 21                         ; candidate.py:34:21
	sl_mov_b64 s[2:3], tcr
	.loc	1 34 36 is_stmt 0               ; candidate.py:34:36
	ml_cmp_gt_i32 tcr, s19, v6
	.loc	1 35 54 is_stmt 1               ; candidate.py:35:54
	ml_bfe2_b32 v13, tid, 0x25
	ml_anyop3_b32 v7, 62, v7, v13, 0xfffffff8
	.loc	1 34 36                         ; candidate.py:34:36
	sl_mov_b64 s[4:5], tcr
	.loc	1 35 15                         ; candidate.py:35:15
	ml_addo_u32 {v9, tcr}, s16, v9
	.loc	1 34 25                         ; candidate.py:34:25
	sl_and_b64 {s[6:7], wcr}, s[0:1], s[4:5]
	sl_and_b64 {s[4:5], wcr}, s[2:3], s[4:5]
	.loc	1 35 54                         ; candidate.py:35:54
	sl_mov_b32 s0, 0x1000504
	.loc	1 35 15 is_stmt 0               ; candidate.py:35:15
	ml_addc_i32 v8, v10, v8, tcr
	.loc	1 35 36                         ; candidate.py:35:36
	ml_shl_b32 v10, v6, 0x1
	ml_addo_u32 {v9, tcr}, v10, v9
	.loc	1 35 54                         ; candidate.py:35:54
	ml_byte_permute_b32 v0, v1, v0, s0
	ml_byte_permute_b32 v1, v3, v2, s0
	ml_and_b32 v2, tid, 0x1
	.loc	1 35 36                         ; candidate.py:35:36
	ml_addc_i32 v8, 0, v8, tcr
	.loc	1 35 54                         ; candidate.py:35:54
	ml_cmp_eq_u32 tcr, v2, 0x0
	ml_mov_b32 v2, 0x7632
	ml_mov_b32 v3, 0x5410
	ml_csel_b32 v11, v3, v2, tcr
	ml_csel_b32 v12, v2, v3, tcr
	sl_mov_b32 s1, 0x2010200
	ml_byte_permute_b32 v11, v11, v11, s1
	ml_pk_shl_b16 v11, v11, 0x40004
	ml_pk_srl_b8 v11, v11, 0x40004
	ml_byte_permute_b32 v11, v0, v1, v11
	ml_byte_permute_b32 v12, v12, v12, s1
	ml_pk_shl_b16 v12, v12, 0x40004
	ml_slb_shuffle_rtn_b32 v11, v11, v7
	ml_pk_srl_b8 v12, v12, 0x40004
	ml_byte_permute_b32 v0, v0, v1, v12
	ml_xor_b32 v1, v7, 0x1
	ml_slb_shuffle_rtn_b32 v0, v0, v1
	.loc	1 35 36                         ; candidate.py:35:36
	ml_add_i32 v1, v6, v4
	ml_add_i32 v4, v10, v5
	.loc	1 35 54                         ; candidate.py:35:54
	ml_and_b32 v5, tid, 0x20
	ml_cmp_eq_u32 tcr, v5, 0x0
	ml_mov_b32 v5, 0x1054
	ml_csel_b32 v3, v3, v5, tcr
	ml_mov_b32 v5, 0x3276
	ml_csel_b32 v2, v2, v5, tcr
	ml_byte_permute_b32 v3, v3, v3, s1
	ml_pk_shl_b16 v3, v3, 0x40004
	ml_pk_srl_b8 v3, v3, 0x40004
	.loc	1 35 47                         ; candidate.py:35:47
	ml_mov_v2s_b32 s0, v9, 0x0
	.loc	1 35 54                         ; candidate.py:35:54
	ml_byte_permute_b32 v2, v2, v2, s1
	ml_pk_shl_b16 v2, v2, 0x40004
	.loc	1 35 47                         ; candidate.py:35:47
	ml_mov_v2s_b32 s1, v8, 0x0
	ml_mov_b32 v5, s0
	ml_sub_i32 v5, v9, v5
	sl_mov_b32 s3, s26
	ml_shl_b32 v1, v1, 0x1
	.loc	1 35 54                         ; candidate.py:35:54
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v3, v11, v0, v3
	.loc	1 35 47                         ; candidate.py:35:47
	ml_sub_i32 v1, v4, v1
	ml_mov_v2s_b32 s2, v1, 0x0
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v3, s[0:3], signed v5, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 35 54                         ; candidate.py:35:54
	ml_pk_srl_b8 v1, v2, 0x40004
	ml_byte_permute_b32 v0, v11, v0, v1
	.loc	1 35 47                         ; candidate.py:35:47
	ml_add_i32 v1, s2, v5
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v0, s[0:3], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 35 4                          ; candidate.py:35:4
	sl_eop 
.Ltmp5:
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	fixed_address_mm.kd
	.type	fixed_address_mm.kd,@object
	.size	fixed_address_mm.kd, 64
fixed_address_mm.kd:
	.asciz	"\000\000\000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	fixed_address_mm@rel64-fixed_address_mm.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	536838
	.asciz	"\003\000\264\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	fixed_address_mm, .Lfunc_end0-fixed_address_mm
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 2056
; NumSgprs: 38
; NumVgprs: 25
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 4
; VGPRBlocks: 6
; NumSGPRsForWarpsPerNU: 34
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
	.long	214                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0xcf DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"candidate.py"                  ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/workspace/experiments/minicpm-s2/framework/20261026T174414509153Z-main594-m32-fixed-address-component/source" ; DW_AT_comp_dir
	.byte	0
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.byte	2                               ; Abbrev [2] 0xa4:0x13 DW_TAG_subprogram
	.ascii	"fixed_address_mm"              ; DW_AT_name
	.byte	0
	.byte	1                               ; DW_AT_inline
	.byte	3                               ; Abbrev [3] 0xb7:0x22 DW_TAG_subprogram
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.long	164                             ; DW_AT_abstract_origin
	.byte	4                               ; Abbrev [4] 0xcc:0xc DW_TAG_inlined_subroutine
	.long	164                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges0                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	26                              ; DW_AT_call_line
	.byte	31                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	0                               ; End Of Children Mark
	.section	.debug_ranges,"",@progbits
.Ldebug_ranges0:
	.quad	.Ltmp1-.Lfunc_begin0
	.quad	.Ltmp2-.Lfunc_begin0
	.quad	.Ltmp3-.Lfunc_begin0
	.quad	.Ltmp4-.Lfunc_begin0
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
    .name:           fixed_address_mm
    .private_segment_fixed_size: 0
    .sgpr_count:     38
    .sgpr_spill_count: 0
    .symbol:         fixed_address_mm.kd
    .vgpr_count:     25
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
