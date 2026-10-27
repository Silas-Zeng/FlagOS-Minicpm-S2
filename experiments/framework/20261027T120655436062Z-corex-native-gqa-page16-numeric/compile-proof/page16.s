	.text
	.globl	corex_native_page16             ; -- Begin function corex_native_page16
	.p2align	3
	.type	corex_native_page16,@function
	.iluvatar_kernel corex_native_page16
corex_native_page16:                    ; @corex_native_page16
	.iluvatar_kernel_code_t
		iluvatar_code_version_major = 1
		iluvatar_code_version_minor = 3
		iluvatar_machine_kind = 1
		iluvatar_machine_version_major = 1
		iluvatar_machine_version_minor = 1
		iluvatar_machine_version_stepping = 0
		kernel_code_entry_byte_offset = 256
		kernel_code_prefetch_byte_size = 0
		granulated_workitem_vgpr_count = 8
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
		granulated_slb_size = 8
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
		workgroup_group_segment_byte_size = 8192
		kernarg_segment_byte_size = 96
		workgroup_fbarrier_count = 0
		warp_sgpr_count = 48
		workitem_vgpr_count = 33
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
	ml_mov_b32 v1, tid
	sl_lsa_load_b32x16 s[12:27], s[4:5], noreg, #0, ca
	ml_srl_b32 v0, tid, 0x4
	ml_and_b32 v2, tid, 0xf
	sl_mull_u32 s10, s6, 0x400
	ml_shl_b32 v3, v2, 0x1
	ml_shl_b32 v4, v0, 0x9
	sl_mov_b32 s11, 0x0
	sl_shl_b64 {s[0:1], wcr}, s[10:11], 0x1
	ml_or_b32 v16, v4, v3
	sl_mov_b32 s3, 0xffffffff
	sl_mull_u32 s10, s6, 0x80
	sl_shl_b64 {s[28:29], wcr}, s[10:11], 0x1
	sl_wait smcnt(0)
	sl_add_i64 s[0:1], s[12:13], s[0:1]
	ml_lsa_load_ushort v17, s[0:3], signed v16, noreg, #0, ca
	sl_mov_b64 s[12:13], s[18:19]
	sl_lsa_load_b32x1 s12, s[12:13], noreg, #0, ca
	sl_mov_b32 s10, s11
	ml_lsa_load_ushort v11, s[0:3], signed v16, noreg, #32, ca
	sl_mov_b32 s31, 0x400
	sl_mov_b32 s30, 0x40
	sl_mov_b32 s33, 0x800
	ml_lsa_load_ushort v18, s[0:3], signed v16, noreg, #256, ca
	sl_mov_b32 s32, 0x80
	sl_mov_b32 s35, 0xc00
	sl_mov_b32 s34, 0xc0
	ml_lsa_load_ushort v12, s[0:3], signed v16, noreg, #288, ca
	sl_wait smcnt(0)
	sl_sra_b32 {s13, wcr}, s12, 0x1f
	sl_shl_b64 {s[18:19], wcr}, s[12:13], 0xe
	ml_lsa_load_ushort v9, s[0:3], signed v16, noreg, #64, ca
	sl_add_i64 s[12:13], s[14:15], s[18:19]
	sl_add_i64 s[12:13], s[12:13], s[28:29]
	sl_mov_b32 s15, 0x200
	ml_lsa_load_ushort v10, s[0:3], signed v16, noreg, #320, ca
	sl_mov_b32 s14, s3
	sl_sme_load_16x1b64_col s[12:15], s[10:11], 0x0, 0x0, 0x0, 0x1
	sl_sme_load_16x1b64_col s[12:15], s[30:31], 0x0, 0x0, 0x0, 0x1
	ml_lsa_load_ushort v6, s[0:3], signed v16, noreg, #96, ca
	sl_sme_load_16x1b64_col s[12:15], s[32:33], 0x0, 0x0, 0x0, 0x1
	sl_sme_load_16x1b64_col s[12:15], s[34:35], 0x0, 0x0, 0x0, 0x1
	sl_mov_b32 s31, 0x1400
	ml_lsa_load_ushort v7, s[0:3], signed v16, noreg, #352, ca
	sl_mov_b32 s33, 0x1800
	sl_mov_b32 s35, 0x1c00
	ml_lsa_load_ushort v3, s[0:3], signed v16, noreg, #128, ca
	ml_lsa_load_ushort v8, s[0:3], signed v16, noreg, #384, ca
	ml_lsa_load_ushort v4, s[0:3], signed v16, noreg, #160, ca
	ml_lsa_load_ushort v5, s[0:3], signed v16, noreg, #416, ca
	ml_lsa_load_ushort v13, s[0:3], signed v16, noreg, #192, ca
	ml_lsa_load_ushort v14, s[0:3], signed v16, noreg, #448, ca
	ml_lsa_load_ushort v15, s[0:3], signed v16, noreg, #224, ca
	ml_lsa_load_ushort v16, s[0:3], signed v16, noreg, #480, ca
	sl_wait g2scnt(0)
	sl_add_i64 s[0:1], s[16:17], s[18:19]
	sl_add_i64 s[12:13], s[0:1], s[28:29]
	sl_mov_b32 s1, 0x1000
	sl_mov_b32 s0, s11
	sl_sme_load_16x1b64_rowxfb16 s[12:15], s[0:1], 0x0, 0x0, 0x0, 0x1
	sl_sme_load_16x1b64_rowxfb16 s[12:15], s[30:31], 0x0, 0x0, 0x0, 0x1
	sl_sme_load_16x1b64_rowxfb16 s[12:15], s[32:33], 0x0, 0x0, 0x0, 0x1
	sl_sme_load_16x1b64_rowxfb16 s[12:15], s[34:35], 0x0, 0x0, 0x0, 0x1
	sl_lsa_load_b32x16 s[28:43], s[4:5], noreg, #64, ca
	sl_wait smcnt(0) g2scnt(0)
	sl_mov_b32 s1, s31
	sl_mov_b32 s0, s30
	sl_wait vmcnt(0)
	sl_barrier 
	sl_mull_u32 s10, s6, 0x800
	sl_sub_u64 s[2:3], s[8:9], s[8:9]
	sl_mov_b32 s7, 0xfff00004
BB0_1:                                  ; =>This Inner Loop Header: Depth=1
	ml_shl_b32 v19, v1, 0x2
	ml_slb_load_b32x1  v19, v19, noreg, #0, null
	sl_shl_b64 {s[4:5], wcr}, s[10:11], 0x2
	ml_add_i32 v20, v1, 0x40
	ml_cmp_gt_u32 tcr, v1, 0x7bf
	sl_add_i64 s[4:5], s[34:35], s[4:5]
	sl_xor_b64 {s[2:3], wcr}, tcr, s[2:3]
	sl_wait lmcnt(0)
	ml_lsa_store_dword v19, s[4:7], unsigned v1, noreg, #0, wb|mie
	ml_mov_b32 v1, v20
	sl_andn1_savetmsk_b64 s[4:5], s[2:3], tmsk
	sl_cbr_tmsknz BB0_1
; %bb.2:
	sl_or_b64 {tmsk, wcr}, tmsk, s[2:3]
	sl_mov_b32 s2, 0x1000504
	ml_byte_permute_b32 v21, v18, v17, s2
	ml_shl_b32 v1, tid, 0x6
	ml_and_b32 v26, v1, 0x300
	ml_shl_b32 v1, tid, 0x2
	ml_or_b32 v27, v1, v26
	ml_slb_load_b32x1  v23, v27, noreg, #0, null
	ml_xor_b32 v28, tid, 0x4
	ml_shl_b32 v17, v28, 0x2
	ml_or_b32 v29, v17, v26
	ml_slb_load_b32x1  v24, v29, noreg, #0, null
	ml_mov_b32 v22, v21
	ml_mov_b32 v17, 0x0
	ml_mov_b32 v18, 0x0
	ml_xor_b32 v30, tid, 0x8
	ml_shl_b32 v19, v30, 0x2
	ml_or_b32 v31, v19, v26
	ml_slb_load_b32x1  v25, v31, noreg, #0, null
	ml_mov_b32 v19, 0x0
	ml_mov_b32 v20, 0x0
	ml_anyop3_b32 v32, 48, v1, v26, 0xf6
	ml_slb_load_b32x1  v26, v32, noreg, #0, null
	sl_mov_b32 s5, 0x400
	ml_byte_permute_b32 v11, v12, v11, s2
	ml_mov_b32 v12, v11
	ml_byte_permute_b32 v9, v10, v9, s2
	ml_mov_b32 v10, v9
	sl_mov_b32 s7, 0x800
	ml_byte_permute_b32 v6, v7, v6, s2
	ml_mov_b32 v7, v6
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[17:20], v[21:22], v[23:24], v[17:20]
	sl_mov_b32 s10, 0xc00
	ml_slb_load_b32x1  v21, v27, s5, #0, null
	sl_mull_u32 s4, s6, 0x8
	sl_mov_b32 s31, 0xfff00004
	sl_mov_b32 s35, 0xfff00002
	ml_slb_load_b32x1  v22, v29, s5, #0, null
	ml_cmp_eq_u32 tcr, v2, 0x0
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[17:20], v[11:12], v[25:26], v[17:20]
	ml_slb_load_b32x1  v11, v31, s5, #0, null
	ml_slb_load_b32x1  v12, v32, s5, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[17:20], v[9:10], v[21:22], v[17:20]
	ml_slb_load_b32x1  v9, v27, s7, #0, null
	ml_slb_load_b32x1  v10, v29, s7, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[17:20], v[6:7], v[11:12], v[17:20]
	ml_slb_load_b32x1  v6, v31, s7, #0, null
	ml_slb_load_b32x1  v7, v32, s7, #0, null
	ml_byte_permute_b32 v11, v8, v3, s2
	ml_mov_b32 v12, v11
	ml_slb_load_b32x1  v3, v27, s10, #0, null
	ml_byte_permute_b32 v8, v5, v4, s2
	ml_slb_load_b32x1  v4, v29, s10, #0, null
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[17:20], v[11:12], v[9:10], v[17:20]
	ml_slb_load_b32x1  v5, v31, s10, #0, null
	ml_mov_b32 v9, v8
	ml_xor_b32 v10, tid, 0x1
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[17:20], v[8:9], v[6:7], v[17:20]
	ml_slb_load_b32x1  v6, v32, s10, #0, null
	ml_byte_permute_b32 v7, v14, v13, s2
	ml_mov_b32 v8, v7
	ml_xor_b32 v9, tid, 0x2
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[17:20], v[7:8], v[3:4], v[17:20]
	ml_byte_permute_b32 v3, v16, v15, s2
	ml_mov_b32 v4, v3
	sl_mov_b64 s[2:3], s[30:31]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[17:20], v[3:4], v[5:6], v[17:20]
	ml_mul_f32 v4, s20, v17
	ml_slb_shuffle_rtn_b32 v3, v4, v30
	ml_mul_f32 v7, s20, v18
	ml_slb_shuffle_rtn_b32 v5, v7, v30
	sl_wait lmcnt(1)
	ml_max_f32 v3, v4, v3
	ml_slb_shuffle_rtn_b32 v6, v3, v28
	sl_wait lmcnt(1)
	ml_max_f32 v5, v7, v5
	ml_slb_shuffle_rtn_b32 v8, v5, v28
	sl_wait lmcnt(1)
	ml_max_f32 v3, v3, v6
	ml_slb_shuffle_rtn_b32 v6, v3, v9
	sl_wait lmcnt(1)
	ml_max_f32 v5, v5, v8
	ml_slb_shuffle_rtn_b32 v8, v5, v9
	sl_wait lmcnt(1)
	ml_max_f32 v3, v3, v6
	ml_slb_shuffle_rtn_b32 v6, v3, v10
	sl_wait lmcnt(1)
	ml_max_f32 v5, v5, v8
	ml_slb_shuffle_rtn_b32 v8, v5, v10
	sl_wait lmcnt(1)
	ml_max_f32 v6, v3, v6
	ml_sub_f32 v3, v4, v6
	ml_exp_f32 v11, v3
	sl_wait lmcnt(0)
	ml_max_f32 v5, v5, v8
	ml_sub_f32 v3, v7, v5
	ml_exp_f32 v8, v3
	ml_slb_shuffle_rtn_b32 v3, v11, v30
	ml_slb_shuffle_rtn_b32 v12, v8, v30
	sl_wait lmcnt(1)
	ml_add_f32 v13, v11, v3
	ml_slb_shuffle_rtn_b32 v14, v13, v28
	ml_add_i32 v3, s4, v0
	ml_shl_b32 v16, v3, 0x4
	sl_wait lmcnt(1)
	ml_add_f32 v12, v8, v12
	ml_slb_shuffle_rtn_b32 v15, v12, v28
	ml_or_b32 v16, v16, v2
	ml_lsa_store_dword v4, s[28:31], unsigned v16, noreg, #0, wb|mie
	ml_add_i32 v4, v3, 0x4
	sl_wait lmcnt(1)
	ml_add_f32 v13, v13, v14
	ml_slb_shuffle_rtn_b32 v14, v13, v9
	sl_wait lmcnt(1)
	ml_add_f32 v12, v12, v15
	ml_slb_shuffle_rtn_b32 v15, v12, v9
	ml_shl_b32 v9, v4, 0x4
	ml_or_b32 v17, v9, v2
	ml_lsa_store_dword v7, s[28:31], unsigned v17, noreg, #0, wb|mie
	ml_lsa_store_dword v11, s[0:3], unsigned v16, noreg, #0, wb|mie
	ml_lsa_store_dword v8, s[0:3], unsigned v17, noreg, #0, wb|mie
	ml_cvt_bf16_f32  v8, v8
	sl_wait lmcnt(1)
	ml_add_f32 v7, v13, v14
	ml_slb_shuffle_rtn_b32 v9, v7, v10
	sl_wait lmcnt(0)
	ml_add_f32 v9, v7, v9
	ml_add_f32 v7, v12, v15
	ml_slb_shuffle_rtn_b32 v10, v7, v10
	sl_wait lmcnt(0)
	ml_add_f32 v10, v7, v10
	ml_cvt_bf16_f32  v7, v11
	ml_lsa_store_short v7, s[32:35], unsigned v16, noreg, #0, wb|mie
	ml_lsa_store_short v8, s[32:35], unsigned v17, noreg, #0, wb|mie
	sl_and_savetmsk_b64 s[0:1], tcr, tmsk
	; mask branch BB0_4
BB0_3:
	ml_mul_f32 v6, v6, 0x3f317218
	sl_mov_b32 s5, 0x0
	sl_shl_b64 {s[2:3], wcr}, s[4:5], 0x2
	sl_add_i64 s[28:29], s[24:25], s[2:3]
	ml_lsa_store_dword v6, s[28:31], unsigned v0, noreg, #0, wb|mie
	ml_mul_f32 v5, v5, 0x3f317218
	ml_lsa_store_dword v5, s[28:31], unsigned v0, noreg, #16, wb|mie
	sl_add_i64 s[28:29], s[26:27], s[2:3]
	ml_lsa_store_dword v9, s[28:31], unsigned v0, noreg, #0, wb|mie
	ml_lsa_store_dword v10, s[28:31], unsigned v0, noreg, #16, wb|mie
BB0_4:
	sl_or_b64 {tmsk, wcr}, tmsk, s[0:1]
	ml_and_b32 v0, tid, 0x10
	ml_cmp_eq_u32 tcr, v0, 0x0
	ml_csel_b32 v5, v7, v8, tcr
	ml_and_b32 v5, v5, 0xffff
	ml_shl_b32 v0, v0, 0x1
	ml_and_b32 v9, tid, 0x20
	ml_srl_b32 v6, v9, 0x1
	ml_anyop3_b32 v0, v0, v6, v2, 0xfffffffe
	ml_slb_shuffle_rtn_b32 v5, v5, v0
	ml_csel_b32 v6, v8, v7, tcr
	ml_and_b32 v6, v6, 0xffff
	ml_xor_b32 v0, v0, 0x10
	ml_slb_shuffle_rtn_b32 v6, v6, v0
	ml_cmp_ne_u32 tcr, v9, 0x0
                                        ; implicit-def: $vgpr0
	sl_and_savetmsk_b64 s[0:1], tcr, tmsk
	sl_xor_b64 {s[0:1], wcr}, tmsk, s[0:1]
	; mask branch BB0_6
BB0_5:
	sl_wait lmcnt(1)
	ml_shl_b32 v0, v5, 0x10
	sl_wait lmcnt(0)
	ml_or_b32 v0, v6, v0
                                        ; implicit-def: $vgpr6
                                        ; implicit-def: $vgpr5
BB0_6:
	sl_or_savetmsk_b64 s[0:1], s[0:1], tmsk
	sl_xor_savetmsk_b64 s[2:3], s[0:1], tmsk
	; mask branch BB0_8
BB0_7:
	ml_shl_b32 v0, v6, 0x10
	ml_or_b32 v0, v0, v5
BB0_8:
	sl_or_b64 {tmsk, wcr}, tmsk, s[0:1]
	sl_mov_b32 s2, 0x1000
	ml_slb_blkload_x1  v13, noreg, s2, #0, null
	ml_xor_b32 v21, v1, 0x80
	ml_mov_b32 v1, v0
	ml_mov_b32 v5, 0x0
	ml_slb_blkload_x1  v14, noreg, s2, #256, null
	ml_mov_b32 v6, 0x0
	ml_mov_b32 v7, 0x0
	ml_mov_b32 v8, 0x0
	ml_slb_load_b32x1  v17, v21, s2, #512, null
	sl_mov_b32 s3, 0xfff00004
	ml_shl_b32 v3, v3, 0x7
	sl_mov_b64 s[0:1], s[22:23]
	ml_slb_load_b32x1  v18, v21, s2, #768, null
	ml_or_b32 v22, v3, v2
	ml_shl_b32 v3, v4, 0x7
	ml_or_b32 v4, v3, v2
	sl_mov_b32 s4, 0x1400
	ml_slb_blkload_x1  v2, noreg, s4, #0, null
	sl_mov_b32 s5, 0x1800
	sl_mov_b32 s6, 0x1c00
	ml_slb_blkload_x1  v3, noreg, s4, #256, null
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[9:12], v[0:1], v[13:14], v[5:8]
	ml_slb_blkload_x1  v19, noreg, s5, #0, null
	ml_slb_blkload_x1  v20, noreg, s5, #256, null
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[13:16], v[0:1], v[17:18], v[5:8]
	ml_slb_load_b32x1  v17, v21, s4, #512, null
	ml_lsa_store_dword v11, s[0:3], unsigned v22, noreg, #0, wb|mie
	ml_lsa_store_dword v12, s[0:3], unsigned v4, noreg, #0, wb|mie
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[9:12], v[0:1], v[2:3], v[5:8]
	ml_lsa_store_dword v15, s[0:3], unsigned v22, noreg, #64, wb|mie
	ml_slb_load_b32x1  v18, v21, s4, #768, null
	ml_lsa_store_dword v16, s[0:3], unsigned v4, noreg, #64, wb|mie
	ml_lsa_store_dword v11, s[0:3], unsigned v22, noreg, #128, wb|mie
	ml_lsa_store_dword v12, s[0:3], unsigned v4, noreg, #128, wb|mie
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[9:12], v[0:1], v[19:20], v[5:8]
	ml_slb_load_b32x1  v2, v21, s5, #512, null
	ml_slb_load_b32x1  v3, v21, s5, #768, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[13:16], v[0:1], v[17:18], v[5:8]
	ml_slb_blkload_x1  v17, noreg, s6, #0, null
	ml_slb_blkload_x1  v18, noreg, s6, #256, null
	ml_lsa_store_dword v15, s[0:3], unsigned v22, noreg, #192, wb|mie
	ml_lsa_store_dword v16, s[0:3], unsigned v4, noreg, #192, wb|mie
	ml_lsa_store_dword v11, s[0:3], unsigned v22, noreg, #256, wb|mie
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[13:16], v[0:1], v[2:3], v[5:8]
	ml_slb_load_b32x1  v19, v21, s6, #512, null
	ml_slb_load_b32x1  v20, v21, s6, #768, null
	ml_lsa_store_dword v12, s[0:3], unsigned v4, noreg, #256, wb|mie
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[9:12], v[0:1], v[17:18], v[5:8]
	ml_lsa_store_dword v15, s[0:3], unsigned v22, noreg, #320, wb|mie
	ml_lsa_store_dword v16, s[0:3], unsigned v4, noreg, #320, wb|mie
	ml_lsa_store_dword v11, s[0:3], unsigned v22, noreg, #384, wb|mie
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[5:8], v[0:1], v[19:20], v[5:8]
	ml_lsa_store_dword v12, s[0:3], unsigned v4, noreg, #384, wb|mie
	ml_lsa_store_dword v7, s[0:3], unsigned v22, noreg, #448, wb|mie
	ml_lsa_store_dword v8, s[0:3], unsigned v4, noreg, #448, wb|mie
	sl_eop 
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	corex_native_page16.kd
	.type	corex_native_page16.kd,@object
	.size	corex_native_page16.kd, 64
corex_native_page16.kd:
	.asciz	"\000 \000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	corex_native_page16@rel64-corex_native_page16.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	536904
	.asciz	"#\000\224\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	corex_native_page16, .Lfunc_end0-corex_native_page16
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 2624
; NumSgprs: 48
; NumVgprs: 33
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 8192 bytes/workgroup (compile time only)
; SGPRBlocks: 5
; VGPRBlocks: 8
; NumSGPRsForWarpsPerNU: 44
; NumVGPRsForWarpsPerNR: 33
; ReqNTIDx: 0
; MaxNTIDx: 0
; MinCTASm: 1
; ActiveWarp: 7
; WarpLimiterHint : 0
	.type	gPrintBuf,@object               ; @gPrintBuf
	.data
	.weak	gPrintBuf
	.p2align	3, 0x0
gPrintBuf:
	.quad	0
	.size	gPrintBuf, 8

	.type	gAssertReason,@object           ; @gAssertReason
	.weak	gAssertReason
	.p2align	3, 0x0
gAssertReason:
	.quad	0
	.size	gAssertReason, 8

	.ident	"clang version 22.1.0git (4.5.0.20260707 a526c4d94919b0feb06f49a88a749e075a7f5cf3)"
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
      - .name:           KArg_4
        .offset:         32
        .size:           4
        .value_kind:     by_value
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
      - .address_space:  global
        .name:           KArg_9
        .offset:         72
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_10
        .offset:         80
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_11
        .offset:         88
        .size:           8
        .value_kind:     global_buffer
    .group_segment_fixed_size: 8192
    .kernarg_segment_align: 8
    .kernarg_segment_size: 96
    .max_flat_workgroup_size: 0
    .name:           corex_native_page16
    .private_segment_fixed_size: 0
    .sgpr_count:     48
    .sgpr_spill_count: 0
    .symbol:         corex_native_page16.kd
    .vgpr_count:     33
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
