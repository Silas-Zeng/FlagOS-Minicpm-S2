	.section	.text._Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_,"axG",@progbits,_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_,comdat
	.globl	_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_ ; -- Begin function _Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_
	.p2align	3
	.type	_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_,@function
	.iluvatar_kernel _Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_
_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_: ; @_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_
	.iluvatar_kernel_code_t
		iluvatar_code_version_major = 1
		iluvatar_code_version_minor = 3
		iluvatar_machine_kind = 1
		iluvatar_machine_version_major = 1
		iluvatar_machine_version_minor = 1
		iluvatar_machine_version_stepping = 0
		kernel_code_entry_byte_offset = 256
		kernel_code_prefetch_byte_size = 0
		granulated_workitem_vgpr_count = 18
		granulated_warp_sgpr_count = 7
		float_mode = 12
		debug_mode = 0
		has_mbar = 0
		user_sgpr_count = 6
		enable_sgpr_workgroup_id_x = 1
		enable_sgpr_workgroup_id_y = 1
		enable_sgpr_workgroup_id_z = 1
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
		kernarg_segment_byte_size = 136
		workgroup_fbarrier_count = 0
		warp_sgpr_count = 62
		workitem_vgpr_count = 76
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
	;  blockIdx.x : s6  blockIdx.y : s7  blockIdx.z : s8
	sl_mov_b32 s0, s6
	sl_lsa_load_b32x16 s[28:43], s[4:5], noreg, #0, ca
	sl_mov_b32 s44, 0x0
	sl_mov_b32 s1, s44
	sl_shl_b64 {s[2:3], wcr}, s[0:1], 0x2
	sl_wait smcnt(0)
	sl_add_i64 s[12:13], s[34:35], s[2:3]
	sl_lsa_load_b32x1 s3, s[12:13], noreg, #0, ca
	sl_wait smcnt(0)
	sl_add_i32 s1, s3, 0x3f
	sl_srl_b32 {s6, wcr}, s1, 0x6
	sl_mull_u32 s2, s6, s8
	sl_mull_u32 s9, s2, 0x10
	sl_cmp_lt_i32 wcr, s9, s3
	sl_cbr_wcrz BB0_31
; %bb.1:
	ml_mov_b32 v55, tid
	sl_lsa_load_b32x16 s[12:27], s[4:5], noreg, #64, ca
	ml_srl_b32 v0, tid, 0x4
	sl_mull_u32 s1, s7, 0x8
	ml_shl_b32 v0, v0, 0x1
	ml_add_i32 v2, s1, v0
	ml_and_b32 v8, tid, 0xf
	sl_mull_u32 s39, s43, s0
	sl_mul_u64_u32 s[34:35], s42, s0
	sl_add_i32 s35, s35, s39
	ml_shl_b32 v57, v8, 0x1
	sl_shl_b64 {s[34:35], wcr}, s[34:35], 0x1
	sl_add_i64 s[28:29], s[28:29], s[34:35]
	sl_wait smcnt(0)
	ml_mul_u64_u32 v[0:1], s13, v2
	sl_mov_b32 s34, 0xc0
	sl_add_i32 s6, s2, s6
	sl_mull_u32 s6, s6, 0x10
	ml_mul_u64_u32 v[1:2], s12, v2
	sl_shl_b64 {s[12:13], wcr}, s[12:13], 0x1
	sl_min_i32 s39, s6, s3
	sl_sub_i32 s3, s39, s9
	ml_mov_b32 v3, s29
	sl_mov_b32 s29, 0x1000504
	ml_add_i32 v0, v2, v0
	ml_shl_b32 v2, v1, 0x1
	ml_addo_u32 {v2, tcr}, s28, v2
	ml_srl_b32 v1, v1, 0x1f
	ml_shl_b32 v0, v0, 0x1
	ml_or_b32 v0, v0, v1
	ml_addc_i32 v1, v3, v0, tcr
	ml_addo_u32 {v0, tcr}, v57, v2
	ml_mov_b32 v3, s13
	sl_mov_b32 s13, 0x60
	sl_mov_b32 s28, 0x80
	ml_addc_i32 v1, 0, v1, tcr
	ml_addo_u32 {v2, tcr}, s12, v0
	ml_lsa_load_a64_ushort  v9, v[0:1], kop=0
	sl_mov_b32 s12, 0x40
	ml_mov_b32 v50, 0x0
	ml_addc_i32 v3, v1, v3, tcr
	ml_addo_u32 {v4, tcr}, 32, v0
	ml_lsa_load_a64_ushort  v10, v[2:3], kop=0
	sl_sra_b32 {s6, wcr}, s3, 0x1f
	sl_srl_b32 {s6, wcr}, s6, 0x1c
	ml_addc_i32 v5, 0, v1, tcr
	ml_addo_u32 {v6, tcr}, 32, v2
	ml_lsa_load_a64_ushort  v11, v[4:5], kop=0
	sl_add_i32 s3, s3, s6
	sl_srl_b32 {s3, wcr}, s3, 0x4
	ml_addc_i32 v7, 0, v3, tcr
	ml_addo_u32 {v4, tcr}, s12, v0
	ml_lsa_load_a64_ushort  v12, v[6:7], kop=0
	sl_add_i32 s2, s3, s2
	sl_wait vmcnt(2)
	ml_byte_permute_b32 v46, v10, v9, s29
	ml_addc_i32 v5, 0, v1, tcr
	ml_addo_u32 {v6, tcr}, s12, v2
	ml_lsa_load_a64_ushort  v13, v[4:5], kop=0
	ml_mov_b32 v47, v46
	sl_mull_u32 s56, s2, 0x10
	ml_addc_i32 v7, 0, v3, tcr
	ml_addo_u32 {v4, tcr}, s13, v0
	ml_lsa_load_a64_ushort  v14, v[6:7], kop=0
	sl_mull_u32 s6, s41, s0
	sl_wait vmcnt(2)
	ml_byte_permute_b32 v44, v12, v11, s29
	ml_addc_i32 v5, 0, v1, tcr
	ml_addo_u32 {v6, tcr}, s13, v2
	ml_lsa_load_a64_ushort  v15, v[4:5], kop=0
	sl_mov_b32 s13, 0xa0
	ml_mov_b32 v45, v44
	ml_addc_i32 v7, 0, v3, tcr
	ml_addo_u32 {v4, tcr}, s28, v0
	ml_lsa_load_a64_ushort  v16, v[6:7], kop=0
	sl_mul_u64_u32 s[2:3], s40, s0
	sl_wait vmcnt(2)
	ml_byte_permute_b32 v42, v14, v13, s29
	ml_addc_i32 v5, 0, v1, tcr
	ml_addo_u32 {v6, tcr}, s28, v2
	ml_lsa_load_a64_ushort  v17, v[4:5], kop=0
	ml_mov_b32 v43, v42
	sl_add_i32 s3, s3, s6
	ml_addc_i32 v7, 0, v3, tcr
	ml_addo_u32 {v4, tcr}, s13, v0
	ml_lsa_load_a64_ushort  v18, v[6:7], kop=0
	sl_shl_b64 {s[2:3], wcr}, s[2:3], 0x2
	sl_wait vmcnt(2)
	ml_byte_permute_b32 v40, v16, v15, s29
	ml_addc_i32 v5, 0, v1, tcr
	ml_addo_u32 {v6, tcr}, s13, v2
	sl_mov_b32 s13, 0xe0
	ml_lsa_load_a64_ushort  v19, v[4:5], kop=0
	ml_mov_b32 v41, v40
	ml_addc_i32 v7, 0, v3, tcr
	ml_addo_u32 {v4, tcr}, s34, v0
	ml_lsa_load_a64_ushort  v20, v[6:7], kop=0
	sl_add_i64 s[48:49], s[36:37], s[2:3]
	sl_wait vmcnt(2)
	ml_byte_permute_b32 v38, v18, v17, s29
	ml_addc_i32 v5, 0, v1, tcr
	ml_addo_u32 {v6, tcr}, s34, v2
	ml_lsa_load_a64_ushort  v4, v[4:5], kop=0
	ml_mov_b32 v39, v38
	ml_mov_b32 v53, 0xff800000
	ml_addc_i32 v7, 0, v3, tcr
	ml_addo_u32 {v0, tcr}, s13, v0
	ml_lsa_load_a64_ushort  v5, v[6:7], kop=0
	ml_xor_b32 v60, tid, 0x4
	sl_wait vmcnt(2)
	ml_byte_permute_b32 v36, v20, v19, s29
	ml_addc_i32 v1, 0, v1, tcr
	ml_addo_u32 {v2, tcr}, s13, v2
	ml_lsa_load_a64_ushort  v0, v[0:1], kop=0
	ml_mov_b32 v37, v36
	ml_mov_b32 v16, 0x0
	ml_addc_i32 v3, 0, v3, tcr
	ml_lsa_load_a64_ushort  v1, v[2:3], kop=0
	sl_cmp_lt_i32 wcr, s9, s56
	ml_mov_b32 v17, 0x0
	sl_wait vmcnt(2)
	ml_byte_permute_b32 v34, v5, v4, s29
	ml_mov_b32 v35, v34
	ml_mov_b32 v18, 0x0
	ml_mov_b32 v19, 0x0
	ml_xor_b32 v61, tid, 0x8
	ml_xor_b32 v62, tid, 0x2
	ml_xor_b32 v63, tid, 0x1
	ml_and_b32 v2, tid, 0x20
	ml_xor_b32 v3, tid, 0x20
	sl_wait vmcnt(0)
	ml_byte_permute_b32 v32, v1, v0, s29
	ml_mov_b32 v33, v32
	ml_xor_b32 v0, tid, 0xc
	ml_and_b32 v1, tid, 0x10
	ml_shl_b32 v4, tid, 0x6
	ml_shl_b32 v1, v1, 0x1
	ml_srl_b32 v2, v2, 0x1
	sl_mull_u32 s36, s7, 0x100
	ml_shl_b32 v58, v0, 0x2
	ml_shl_b32 v52, v3, 0x2
	ml_anyop3_b32 v56, v1, v2, v8, 0xfffffffe
	ml_and_b32 v59, v4, 0x300
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
	ml_mov_b32 v28, 0x0
	ml_mov_b32 v29, 0x0
	ml_mov_b32 v30, 0x0
	ml_mov_b32 v31, 0x0
	ml_mov_b32 v54, 0xff800000
	ml_mov_b32 v51, 0x0
	sl_cbr_wcrz BB0_8
; %bb.2:
	ml_mov_b32 v64, 0x0
	ml_and_b32 v0, tid, 0x10
	ml_cmp_eq_u32 tcr, v0, 0x0
	ml_xor_b32 v65, v56, 0x10
	ml_and_b32 v0, tid, 0x20
	ml_mov_b32 v49, 0xff800000
	sl_mov_b64 s[2:3], tcr
	ml_cmp_ne_u32 tcr, v0, 0x0
	sl_mov_b32 s37, s44
	sl_mov_b32 s43, 0x200
	sl_mov_b32 s42, 0xffffffff
	sl_mov_b64 s[6:7], tcr
	sl_mov_b32 s13, 0x400
	sl_mov_b32 s29, 0x800
	sl_mov_b32 s35, 0xc00
	sl_mov_b32 s57, 0x1000
	sl_mov_b32 s51, 0x1400
	sl_mov_b32 s53, 0x1800
	sl_mov_b32 s55, 0x1c00
	ml_or_b32 v66, v58, v59
	ml_shl_b32 v0, tid, 0x2
	ml_or_b32 v67, v0, v59
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v2, 0x0
	ml_mov_b32 v3, 0x0
	ml_mov_b32 v68, 0xff800000
	sl_jump BB0_4
BB0_3:                                  ;   in Loop: Header=BB0_4 Depth=1
	sl_or_b64 {tmsk, wcr}, tmsk, s[40:41]
	ml_sub_f32 v68, v68, v53
	ml_slb_blkload_x1  v71, noreg, s57, #0, null
	ml_exp_f32 v68, v68
	ml_sub_f32 v49, v49, v54
	ml_slb_blkload_x1  v72, noreg, s57, #256, null
	ml_exp_f32 v75, v49
	ml_mov_b32 v49, v48
	ml_mul_f32 v16, v68, v16
	ml_mul_f32 v18, v68, v18
	ml_slb_load_b32x1  v73, v52, s57, #512, null
	ml_mul_f32 v28, v68, v28
	ml_mul_f32 v17, v75, v17
	ml_mul_f32 v19, v75, v19
	ml_slb_load_b32x1  v74, v52, s57, #768, null
	ml_mul_f32 v29, v75, v29
	ml_mul_f32 v30, v68, v30
	ml_mul_f32 v31, v75, v31
	ml_mul_f32 v24, v68, v24
	ml_mul_f32 v25, v75, v25
	ml_mul_f32 v26, v68, v26
	ml_mul_f32 v27, v75, v27
	ml_mul_f32 v20, v68, v20
	ml_mul_f32 v21, v75, v21
	ml_mul_f32 v22, v68, v22
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[48:49], v[71:72], v[16:19]
	ml_slb_blkload_x1  v71, noreg, s51, #0, null
	ml_slb_blkload_x1  v72, noreg, s51, #256, null
	ml_mul_f32 v23, v75, v23
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[48:49], v[73:74], v[28:31]
	ml_slb_load_b32x1  v73, v52, s51, #512, null
	ml_slb_load_b32x1  v74, v52, s51, #768, null
	ml_mul_f32 v12, v68, v12
	ml_mul_f32 v13, v75, v13
	ml_mul_f32 v14, v68, v14
	ml_mul_f32 v15, v75, v15
	ml_mul_f32 v8, v68, v8
	ml_mul_f32 v9, v75, v9
	ml_mul_f32 v10, v68, v10
	ml_mul_f32 v11, v75, v11
	ml_mul_f32 v4, v68, v4
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[48:49], v[71:72], v[24:27]
	ml_slb_blkload_x1  v71, noreg, s53, #0, null
	ml_slb_blkload_x1  v72, noreg, s53, #256, null
	ml_mul_f32 v5, v75, v5
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[48:49], v[73:74], v[20:23]
	ml_slb_load_b32x1  v73, v52, s53, #512, null
	ml_slb_load_b32x1  v74, v52, s53, #768, null
	ml_mul_f32 v6, v68, v6
	ml_mul_f32 v7, v75, v7
	ml_mul_f32 v0, v68, v0
	ml_mul_f32 v1, v75, v1
	ml_mul_f32 v2, v68, v2
	ml_mul_f32 v3, v75, v3
	ml_fma_f32 v50, v50, v68, v69
	ml_fma_f32 v51, v51, v75, v70
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[48:49], v[71:72], v[12:15]
	ml_slb_blkload_x1  v71, noreg, s55, #0, null
	ml_slb_blkload_x1  v72, noreg, s55, #256, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[48:49], v[73:74], v[8:11]
	ml_slb_load_b32x1  v73, v52, s55, #512, null
	ml_slb_load_b32x1  v74, v52, s55, #768, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[48:49], v[71:72], v[4:7]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[48:49], v[73:74], v[0:3]
	sl_barrier 
	sl_add_i32 s9, s9, 0x10
	sl_cmp_lt_i32 wcr, s9, s56
	ml_mov_b32 v49, v54
	ml_mov_b32 v68, v53
	sl_cbr_wcrz BB0_8
BB0_4:                                  ; =>This Inner Loop Header: Depth=1
	sl_sra_b32 {s40, wcr}, s9, 0x4
	sl_sra_b32 {s41, wcr}, s40, 0x1f
	sl_shl_b64 {s[40:41], wcr}, s[40:41], 0x2
	sl_add_i64 s[40:41], s[48:49], s[40:41]
	sl_lsa_load_b32x1 s40, s[40:41], noreg, #0, ca
	sl_mov_b32 s45, s44
	sl_mov_b32 s50, s12
	sl_mov_b32 s52, s28
	sl_mov_b32 s54, s34
	sl_wait smcnt(0)
	sl_sra_b32 {s41, wcr}, s40, 0x1f
	sl_shl_b64 {s[46:47], wcr}, s[40:41], 0xe
	sl_add_i64 s[40:41], s[30:31], s[46:47]
	sl_add_i64 s[40:41], s[40:41], s[36:37]
	sl_sme_load_16x1b64_col s[40:43], s[44:45], 0x0, 0x0, 0x0, 0x1
	sl_sme_load_16x1b64_col s[40:43], s[12:13], 0x0, 0x0, 0x0, 0x1
	sl_sme_load_16x1b64_col s[40:43], s[28:29], 0x0, 0x0, 0x0, 0x1
	sl_sme_load_16x1b64_col s[40:43], s[34:35], 0x0, 0x0, 0x0, 0x1
	sl_wait g2scnt(0)
	sl_add_i64 s[40:41], s[32:33], s[46:47]
	sl_add_i64 s[40:41], s[40:41], s[36:37]
	sl_mov_b32 s45, s57
	sl_sme_load_16x1b64_rowxfb16 s[40:43], s[44:45], 0x0, 0x0, 0x0, 0x1
	sl_sme_load_16x1b64_rowxfb16 s[40:43], s[50:51], 0x0, 0x0, 0x0, 0x1
	sl_sme_load_16x1b64_rowxfb16 s[40:43], s[52:53], 0x0, 0x0, 0x0, 0x1
	sl_sme_load_16x1b64_rowxfb16 s[40:43], s[54:55], 0x0, 0x0, 0x0, 0x1
	sl_wait g2scnt(0)
	sl_barrier 
	sl_mov_b64 tcr, s[2:3]
	ml_slb_load_b32x1  v53, v67, noreg, #0, null
	ml_shl_b32 v48, v60, 0x2
	ml_or_b32 v48, v48, v59
	ml_mov_b32 v69, 0x0
	ml_slb_load_b32x1  v54, v48, noreg, #0, null
	ml_shl_b32 v70, v61, 0x2
	ml_or_b32 v75, v70, v59
	ml_mov_b32 v70, v64
	ml_slb_load_b32x1  v73, v75, noreg, #0, null
	ml_mov_b32 v71, v64
	ml_mov_b32 v72, v64
	ml_slb_load_b32x1  v74, v66, noreg, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[69:72], v[46:47], v[53:54], v[69:72]
	ml_slb_load_b32x1  v53, v67, s13, #0, null
	ml_slb_load_b32x1  v54, v48, s13, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[69:72], v[44:45], v[73:74], v[69:72]
	ml_slb_load_b32x1  v74, v66, s13, #0, null
	ml_slb_load_b32x1  v73, v75, s13, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[69:72], v[42:43], v[53:54], v[69:72]
	ml_slb_load_b32x1  v53, v67, s29, #0, null
	ml_slb_load_b32x1  v54, v48, s29, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[69:72], v[40:41], v[73:74], v[69:72]
	ml_slb_load_b32x1  v74, v66, s29, #0, null
	ml_slb_load_b32x1  v73, v75, s29, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[69:72], v[38:39], v[53:54], v[69:72]
	ml_slb_load_b32x1  v53, v67, s35, #0, null
	ml_slb_load_b32x1  v54, v48, s35, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[69:72], v[36:37], v[73:74], v[69:72]
	ml_slb_load_b32x1  v74, v66, s35, #0, null
	ml_slb_load_b32x1  v73, v75, s35, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[69:72], v[34:35], v[53:54], v[69:72]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[69:72], v[32:33], v[73:74], v[69:72]
	ml_mul_f32 v48, s38, v69
	ml_slb_shuffle_rtn_b32 v53, v48, v61
	ml_mul_f32 v69, s38, v70
	ml_slb_shuffle_rtn_b32 v54, v69, v61
	sl_wait lmcnt(1)
	ml_max_f32 v53, v48, v53
	ml_slb_shuffle_rtn_b32 v70, v53, v60
	sl_wait lmcnt(1)
	ml_max_f32 v54, v69, v54
	ml_slb_shuffle_rtn_b32 v71, v54, v60
	sl_wait lmcnt(1)
	ml_max_f32 v53, v53, v70
	ml_slb_shuffle_rtn_b32 v70, v53, v62
	sl_wait lmcnt(1)
	ml_max_f32 v54, v54, v71
	ml_slb_shuffle_rtn_b32 v71, v54, v62
	sl_wait lmcnt(1)
	ml_max_f32 v53, v53, v70
	ml_slb_shuffle_rtn_b32 v70, v53, v63
	sl_wait lmcnt(1)
	ml_max_f32 v54, v54, v71
	ml_slb_shuffle_rtn_b32 v71, v54, v63
	sl_wait lmcnt(1)
	ml_max_f32 v53, v53, v70
	ml_max_f32 v53, v68, v53
	ml_sub_f32 v48, v48, v53
	sl_wait lmcnt(0)
	ml_max_f32 v54, v54, v71
	ml_exp_f32 v48, v48
	ml_max_f32 v54, v49, v54
	ml_sub_f32 v69, v69, v54
	ml_exp_f32 v69, v69
	ml_slb_shuffle_rtn_b32 v70, v48, v61
	ml_slb_shuffle_rtn_b32 v71, v69, v61
	ml_cvt_bf16_f32  v75, v69
	sl_wait lmcnt(1)
	ml_add_f32 v70, v48, v70
	ml_slb_shuffle_rtn_b32 v72, v70, v60
	ml_cvt_bf16_f32  v48, v48
	sl_wait lmcnt(1)
	ml_add_f32 v71, v69, v71
	ml_slb_shuffle_rtn_b32 v73, v71, v60
	ml_csel_b32 v69, v48, v75, tcr
	ml_and_b32 v69, v69, 0xffff
	ml_csel_b32 v48, v75, v48, tcr
	ml_and_b32 v48, v48, 0xffff
	sl_wait lmcnt(1)
	ml_add_f32 v70, v70, v72
	ml_slb_shuffle_rtn_b32 v72, v70, v62
	sl_wait lmcnt(1)
	ml_add_f32 v73, v71, v73
	ml_slb_shuffle_rtn_b32 v74, v73, v62
	ml_slb_shuffle_rtn_b32 v71, v69, v56
	sl_wait lmcnt(2)
	ml_add_f32 v69, v70, v72
	ml_slb_shuffle_rtn_b32 v70, v69, v63
	sl_wait lmcnt(0)
	ml_add_f32 v69, v69, v70
	ml_add_f32 v70, v73, v74
	ml_slb_shuffle_rtn_b32 v72, v70, v63
	sl_wait lmcnt(0)
	ml_add_f32 v70, v70, v72
	ml_slb_shuffle_rtn_b32 v72, v48, v65
                                        ; implicit-def: $vgpr48
	sl_and_savetmsk_b64 s[40:41], s[6:7], tmsk
	sl_xor_b64 {s[40:41], wcr}, tmsk, s[40:41]
	; mask branch BB0_6
BB0_5:                                  ;   in Loop: Header=BB0_4 Depth=1
	ml_shl_b32 v48, v71, 0x10
	sl_wait lmcnt(0)
	ml_or_b32 v48, v72, v48
                                        ; implicit-def: $vgpr72
                                        ; implicit-def: $vgpr71
BB0_6:                                  ;   in Loop: Header=BB0_4 Depth=1
	sl_or_savetmsk_b64 s[40:41], s[40:41], tmsk
	sl_xor_savetmsk_b64 s[46:47], s[40:41], tmsk
	; mask branch BB0_3
	sl_cbr_tmskaz BB0_3
BB0_7:                                  ;   in Loop: Header=BB0_4 Depth=1
	ml_shl_b32 v48, v72, 0x10
	ml_or_b32 v48, v48, v71
	sl_jump BB0_3
BB0_8:
	sl_cmp_gt_i32 wcr, s39, s56
	sl_cbr_wcrz BB0_28
; %bb.9:
	sl_sra_b32 {s2, wcr}, s56, 0x4
	sl_sra_b32 {s3, wcr}, s2, 0x1f
	sl_shl_b64 {s[2:3], wcr}, s[2:3], 0x2
	sl_add_i64 s[12:13], s[48:49], s[2:3]
	sl_lsa_load_b32x1 s2, s[12:13], noreg, #0, ca
	sl_mov_b32 s37, 0x0
	sl_mov_b32 s43, 0x200
	sl_mov_b32 s42, 0xffffffff
	sl_sub_u64 s[6:7], s[10:11], s[10:11]
	sl_mov_b32 s13, 0xc00
	sl_mov_b32 s12, 0xc0
	sl_wait smcnt(0)
	sl_sra_b32 {s3, wcr}, s2, 0x1f
	sl_shl_b64 {s[28:29], wcr}, s[2:3], 0xe
	sl_add_i64 s[2:3], s[30:31], s[28:29]
	sl_add_i64 s[40:41], s[2:3], s[36:37]
	sl_sme_load_16x1b64_col s[40:43], s[6:7], 0x0, 0x0, 0x0, 0x1
	sl_mov_b32 s3, 0x400
	sl_mov_b32 s2, 0x40
	sl_sme_load_16x1b64_col s[40:43], s[2:3], 0x0, 0x0, 0x0, 0x1
	sl_mov_b32 s7, 0x800
	sl_mov_b32 s6, 0x80
	sl_sme_load_16x1b64_col s[40:43], s[6:7], 0x0, 0x0, 0x0, 0x1
	sl_sme_load_16x1b64_col s[40:43], s[12:13], 0x0, 0x0, 0x0, 0x1
	sl_wait g2scnt(0)
	sl_add_i64 s[28:29], s[32:33], s[28:29]
	sl_add_i64 s[40:41], s[28:29], s[36:37]
	sl_mov_b32 s29, 0x1000
	sl_mov_b32 s28, s37
	sl_sme_load_16x1b64_rowxfb16 s[40:43], s[28:29], 0x0, 0x0, 0x0, 0x1
	sl_mov_b32 s29, 0x1400
	sl_mov_b32 s28, s2
	sl_sme_load_16x1b64_rowxfb16 s[40:43], s[28:29], 0x0, 0x0, 0x0, 0x1
	sl_mov_b32 s29, 0x1800
	sl_mov_b32 s28, s6
	sl_sme_load_16x1b64_rowxfb16 s[40:43], s[28:29], 0x0, 0x0, 0x0, 0x1
	sl_mov_b32 s29, 0x1c00
	sl_mov_b32 s28, s12
	sl_sme_load_16x1b64_rowxfb16 s[40:43], s[28:29], 0x0, 0x0, 0x0, 0x1
	sl_sub_i32 s2, s39, s56
	sl_wait g2scnt(0)
	sl_barrier 
	sl_cmp_lt_u32 wcr, s2, 0x10
	sl_cbr_wcrz BB0_23
; %bb.10:
	ml_shl_b32 v49, tid, 0x5
	ml_shl_b32 v60, tid, 0x1
	ml_mov_b32 v48, 0x0
	sl_sub_u64 s[28:29], s[10:11], s[10:11]
	ml_mov_b32 v61, 0x0
	ml_mov_b32 v62, 0x0
	sl_jump BB0_12
BB0_11:                                 ;   in Loop: Header=BB0_12 Depth=1
	sl_or_b64 {tmsk, wcr}, tmsk, s[30:31]
	ml_add_i32 v63, v55, 0x40
	ml_add_i32 v49, v49, 0x800
	ml_add_i32 v60, v60, 0x80
	ml_add_i32 v61, v61, 0x2
	ml_add_i32 v62, v62, 0x1
	ml_cmp_gt_u32 tcr, v55, 0x3bf
	ml_mov_b32 v55, v63
	sl_xor_b64 {s[28:29], wcr}, tcr, s[28:29]
	sl_andn1_savetmsk_b64 s[30:31], s[28:29], tmsk
	sl_cbr_tmskaz BB0_14
BB0_12:                                 ; =>This Inner Loop Header: Depth=1
	ml_cmp_le_u32 tcr, s2, v62
	sl_and_savetmsk_b64 s[30:31], tcr, tmsk
	; mask branch BB0_11
	sl_cbr_tmskaz BB0_11
BB0_13:                                 ;   in Loop: Header=BB0_12 Depth=1
	ml_srl_b32 v63, v55, 0x1
	ml_and_b32 v63, v63, 0x3fffff80
	ml_and_b32 v64, v49, 0x660
	ml_add_i32 v63, v63, v64
	ml_xor_b32 v64, v61, v60
	ml_anyop3_b32 v63, 16, v64, v63, 0xfffffff8
	ml_srl_b32 v64, v55, 0x5
	ml_anyop3_b32 v64, v64, v60, 8, 0x60
	ml_and_b32 v65, v61, 0x6
	ml_anyop3_b32 v63, v63, v64, v65, 0xfffffffe
	ml_shl_b32 v63, v63, 0x1
	ml_slb_store_b32x1  v48, v63, noreg, #0, null
	sl_jump BB0_11
BB0_14:
	sl_or_b64 {tmsk, wcr}, tmsk, s[28:29]
	ml_add_i32 v49, tid, 0xffffffc0
	ml_srl_b32 v60, tid, 0x4
	ml_shl_b32 v55, v60, 0x6
	ml_or_b32 v55, v55, v57
	ml_shl_b32 v57, v60, 0x8
	sl_sub_u64 s[28:29], s[10:11], s[10:11]
	sl_mov_b32 s6, 0x1000
	ml_mov_b32 v60, 0x0
	sl_jump BB0_17
BB0_15:                                 ;   in Loop: Header=BB0_17 Depth=1
	sl_or_b64 {tmsk, wcr}, tmsk, s[32:33]
BB0_16:                                 ;   in Loop: Header=BB0_17 Depth=1
	sl_or_b64 {tmsk, wcr}, tmsk, s[30:31]
	ml_add_i32 v49, v49, 0x40
	ml_add_i32 v55, v55, 0x100
	ml_add_i32 v48, v48, 0x1
	ml_cmp_gt_u32 tcr, v49, 0x3bf
	ml_add_i32 v57, v57, 0x400
	sl_xor_b64 {s[28:29], wcr}, tcr, s[28:29]
	sl_andn1_savetmsk_b64 s[30:31], s[28:29], tmsk
	sl_cbr_tmskaz BB0_22
BB0_17:                                 ; =>This Inner Loop Header: Depth=1
	ml_shl_b32 v61, v48, 0x4
	ml_and_b32 v62, v61, 0x60
	ml_add_i32 v63, v62, v55
	ml_and_b32 v62, v48, 0xe
	ml_and_b32 v64, v57, 0x700
	ml_and_b32 v61, v61, 0x80
	ml_and_b32 v63, v63, 0x7e
	ml_anyop3_b32 v61, v61, v64, v63, 0xfffffffe
	ml_srl_b32 v61, v61, 0x1
	ml_cmp_le_u32 tcr, s2, v62
	sl_and_savetmsk_b64 s[30:31], tcr, tmsk
	sl_xor_b64 {s[30:31], wcr}, tmsk, s[30:31]
	; mask branch BB0_19
BB0_18:                                 ;   in Loop: Header=BB0_17 Depth=1
	ml_shl_b32 v63, v61, 0x2
                                        ; implicit-def: $vgpr62
                                        ; implicit-def: $vgpr61
	ml_slb_store_b32x1  v60, v63, s6, #0, null
BB0_19:                                 ;   in Loop: Header=BB0_17 Depth=1
	sl_or_savetmsk_b64 s[30:31], s[30:31], tmsk
	sl_xor_savetmsk_b64 s[32:33], s[30:31], tmsk
	; mask branch BB0_16
	sl_cbr_tmskaz BB0_16
BB0_20:                                 ;   in Loop: Header=BB0_17 Depth=1
	ml_add_i32 v62, v62, 0x1
	ml_cmp_le_u32 tcr, s2, v62
	sl_and_savetmsk_b64 s[32:33], tcr, tmsk
	; mask branch BB0_15
	sl_cbr_tmskaz BB0_15
BB0_21:                                 ;   in Loop: Header=BB0_17 Depth=1
	ml_shl_b32 v61, v61, 0x2
	ml_slb_load_b32x1  v62, v61, s6, #0, null
	sl_wait lmcnt(0)
	ml_and_b32 v62, v62, 0xffff
	ml_slb_store_b32x1  v62, v61, s6, #0, null
	sl_jump BB0_15
BB0_22:
	sl_or_b64 {tmsk, wcr}, tmsk, s[28:29]
	sl_wait lmcnt(0)
	sl_barrier 
BB0_23:
	ml_shl_b32 v48, tid, 0x2
	ml_or_b32 v55, v48, v59
	ml_slb_load_b32x1  v48, v55, noreg, #0, null
	ml_xor_b32 v64, tid, 0x4
	ml_shl_b32 v49, v64, 0x2
	ml_or_b32 v65, v49, v59
	ml_slb_load_b32x1  v49, v65, noreg, #0, null
	ml_mov_b32 v60, 0x0
	ml_mov_b32 v61, 0x0
	ml_xor_b32 v66, tid, 0x8
	ml_shl_b32 v57, v66, 0x2
	ml_or_b32 v67, v57, v59
	ml_slb_load_b32x1  v57, v67, noreg, #0, null
	ml_mov_b32 v62, 0x0
	ml_mov_b32 v63, 0x0
	ml_or_b32 v59, v58, v59
	ml_slb_load_b32x1  v58, v59, noreg, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[46:47], v[48:49], v[60:63]
	ml_slb_load_b32x1  v46, v55, s3, #0, null
	ml_slb_load_b32x1  v47, v65, s3, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[44:45], v[57:58], v[60:63]
	ml_slb_load_b32x1  v45, v59, s3, #0, null
	ml_slb_load_b32x1  v44, v67, s3, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[42:43], v[46:47], v[60:63]
	ml_slb_load_b32x1  v42, v55, s7, #0, null
	ml_slb_load_b32x1  v43, v65, s7, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[40:41], v[44:45], v[60:63]
	ml_slb_load_b32x1  v41, v59, s7, #0, null
	ml_slb_load_b32x1  v40, v67, s7, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[38:39], v[42:43], v[60:63]
	ml_slb_load_b32x1  v38, v55, s13, #0, null
	ml_slb_load_b32x1  v39, v65, s13, #0, null
	ml_and_b32 v42, tid, 0x10
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[36:37], v[40:41], v[60:63]
	ml_slb_load_b32x1  v37, v59, s13, #0, null
	ml_slb_load_b32x1  v36, v67, s13, #0, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[34:35], v[38:39], v[60:63]
	ml_xor_b32 v38, tid, 0x2
	ml_xor_b32 v39, tid, 0x1
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[60:63], v[32:33], v[36:37], v[60:63]
	ml_and_b32 v32, tid, 0xf
	ml_mov_b32 v33, 0xff800000
	ml_cmp_gt_u32 tcr, s2, v32
	ml_mul_f32 v32, s38, v60
	ml_csel_b32 v32, v32, v33, tcr
	ml_slb_shuffle_rtn_b32 v34, v32, v66
	ml_mul_f32 v35, s38, v61
	ml_csel_b32 v33, v35, v33, tcr
	ml_cmp_eq_u32 tcr, v42, 0x0
	ml_slb_shuffle_rtn_b32 v35, v33, v66
	sl_wait lmcnt(1)
	ml_max_f32 v34, v32, v34
	ml_slb_shuffle_rtn_b32 v36, v34, v64
	sl_wait lmcnt(1)
	ml_max_f32 v35, v33, v35
	ml_slb_shuffle_rtn_b32 v37, v35, v64
	sl_wait lmcnt(1)
	ml_max_f32 v34, v34, v36
	ml_slb_shuffle_rtn_b32 v36, v34, v38
	sl_wait lmcnt(1)
	ml_max_f32 v35, v35, v37
	ml_slb_shuffle_rtn_b32 v37, v35, v38
	sl_wait lmcnt(1)
	ml_max_f32 v34, v34, v36
	ml_slb_shuffle_rtn_b32 v36, v34, v39
	sl_wait lmcnt(1)
	ml_max_f32 v35, v35, v37
	ml_slb_shuffle_rtn_b32 v37, v35, v39
	sl_wait lmcnt(1)
	ml_max_f32 v34, v34, v36
	ml_max_f32 v34, v53, v34
	ml_sub_f32 v32, v32, v34
	sl_wait lmcnt(0)
	ml_max_f32 v35, v35, v37
	ml_exp_f32 v32, v32
	ml_max_f32 v35, v54, v35
	ml_sub_f32 v33, v33, v35
	ml_exp_f32 v33, v33
	ml_slb_shuffle_rtn_b32 v36, v32, v66
	ml_slb_shuffle_rtn_b32 v37, v33, v66
	sl_wait lmcnt(1)
	ml_add_f32 v36, v32, v36
	ml_slb_shuffle_rtn_b32 v40, v36, v64
	ml_cvt_bf16_f32  v32, v32
	sl_wait lmcnt(1)
	ml_add_f32 v37, v33, v37
	ml_slb_shuffle_rtn_b32 v41, v37, v64
	sl_wait lmcnt(1)
	ml_add_f32 v36, v36, v40
	ml_slb_shuffle_rtn_b32 v40, v36, v38
	sl_wait lmcnt(1)
	ml_add_f32 v37, v37, v41
	ml_slb_shuffle_rtn_b32 v38, v37, v38
	ml_cvt_bf16_f32  v41, v33
	ml_csel_b32 v33, v32, v41, tcr
	ml_and_b32 v33, v33, 0xffff
	ml_slb_shuffle_rtn_b32 v33, v33, v56
	ml_csel_b32 v32, v41, v32, tcr
	ml_and_b32 v32, v32, 0xffff
	sl_wait lmcnt(2)
	ml_add_f32 v36, v36, v40
	ml_slb_shuffle_rtn_b32 v40, v36, v39
	sl_wait lmcnt(2)
	ml_add_f32 v37, v37, v38
	ml_slb_shuffle_rtn_b32 v38, v37, v39
	sl_wait lmcnt(1)
	ml_add_f32 v36, v36, v40
	sl_wait lmcnt(0)
	ml_add_f32 v37, v37, v38
	ml_xor_b32 v38, v56, 0x10
	ml_slb_shuffle_rtn_b32 v38, v32, v38
	ml_and_b32 v32, tid, 0x20
	ml_cmp_ne_u32 tcr, v32, 0x0
                                        ; implicit-def: $vgpr32
	sl_and_savetmsk_b64 s[2:3], tcr, tmsk
	sl_xor_b64 {s[2:3], wcr}, tmsk, s[2:3]
	; mask branch BB0_25
BB0_24:
	ml_shl_b32 v32, v33, 0x10
	sl_wait lmcnt(0)
	ml_or_b32 v32, v38, v32
                                        ; implicit-def: $vgpr38
                                        ; implicit-def: $vgpr33
BB0_25:
	sl_or_savetmsk_b64 s[2:3], s[2:3], tmsk
	sl_xor_savetmsk_b64 s[6:7], s[2:3], tmsk
	; mask branch BB0_27
BB0_26:
	ml_shl_b32 v32, v38, 0x10
	ml_or_b32 v32, v32, v33
BB0_27:
	sl_or_b64 {tmsk, wcr}, tmsk, s[2:3]
	ml_sub_f32 v33, v53, v34
	sl_mov_b32 s2, 0x1000
	ml_slb_blkload_x1  v38, noreg, s2, #0, null
	ml_exp_f32 v42, v33
	ml_sub_f32 v33, v54, v35
	ml_slb_blkload_x1  v39, noreg, s2, #256, null
	ml_exp_f32 v43, v33
	ml_mov_b32 v33, v32
	ml_mul_f32 v16, v42, v16
	ml_mul_f32 v18, v42, v18
	ml_slb_load_b32x1  v40, v52, s2, #512, null
	ml_mul_f32 v28, v42, v28
	ml_mul_f32 v17, v43, v17
	ml_mul_f32 v19, v43, v19
	ml_slb_load_b32x1  v41, v52, s2, #768, null
	ml_mul_f32 v29, v43, v29
	ml_mul_f32 v30, v42, v30
	ml_mul_f32 v31, v43, v31
	sl_mov_b32 s2, 0x1400
	ml_mul_f32 v24, v42, v24
	ml_mul_f32 v25, v43, v25
	ml_mul_f32 v26, v42, v26
	ml_mul_f32 v27, v43, v27
	ml_mul_f32 v20, v42, v20
	ml_mul_f32 v21, v43, v21
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[32:33], v[38:39], v[16:19]
	ml_slb_blkload_x1  v16, noreg, s2, #0, null
	ml_slb_blkload_x1  v17, noreg, s2, #256, null
	ml_mul_f32 v22, v42, v22
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[32:33], v[40:41], v[28:31]
	ml_slb_load_b32x1  v28, v52, s2, #512, null
	ml_slb_load_b32x1  v29, v52, s2, #768, null
	sl_mov_b32 s2, 0x1800
	ml_mul_f32 v23, v43, v23
	ml_mul_f32 v12, v42, v12
	ml_mul_f32 v13, v43, v13
	ml_mul_f32 v14, v42, v14
	ml_mul_f32 v15, v43, v15
	ml_mul_f32 v8, v42, v8
	ml_mul_f32 v9, v43, v9
	ml_mul_f32 v10, v42, v10
	ml_mul_f32 v11, v43, v11
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[32:33], v[16:17], v[24:27]
	ml_slb_blkload_x1  v16, noreg, s2, #0, null
	ml_slb_blkload_x1  v17, noreg, s2, #256, null
	ml_mul_f32 v4, v42, v4
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[32:33], v[28:29], v[20:23]
	ml_slb_load_b32x1  v20, v52, s2, #512, null
	ml_slb_load_b32x1  v21, v52, s2, #768, null
	sl_mov_b32 s2, 0x1c00
	ml_mul_f32 v5, v43, v5
	ml_mul_f32 v6, v42, v6
	ml_mul_f32 v7, v43, v7
	ml_mul_f32 v0, v42, v0
	ml_mul_f32 v1, v43, v1
	ml_mul_f32 v2, v42, v2
	ml_mul_f32 v3, v43, v3
	ml_fma_f32 v50, v50, v42, v36
	ml_fma_f32 v51, v51, v43, v37
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[32:33], v[16:17], v[12:15]
	ml_slb_blkload_x1  v12, noreg, s2, #0, null
	ml_slb_blkload_x1  v13, noreg, s2, #256, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[32:33], v[20:21], v[8:11]
	ml_slb_load_b32x1  v8, v52, s2, #512, null
	ml_slb_load_b32x1  v9, v52, s2, #768, null
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[32:33], v[12:13], v[4:7]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[32:33], v[8:9], v[0:3]
	sl_barrier 
	ml_mov_b32 v53, v34
	ml_mov_b32 v54, v35
BB0_28:
	ml_srl_b32 v0, tid, 0x4
	ml_add_i32 v0, s1, v0
	sl_mull_u32 s1, s15, s0
	ml_mul_u64_u32 v[4:5], s17, v0
	sl_mul_u64_u32 s[2:3], s14, s0
	sl_add_i32 s3, s3, s1
	sl_mull_u32 s1, s19, s8
	ml_mul_u64_u32 v[8:9], s16, v0
	sl_mul_u64_u32 s[6:7], s18, s8
	sl_add_i32 s7, s7, s1
	sl_shl_b64 {s[2:3], wcr}, s[2:3], 0x2
	sl_add_i64 s[2:3], s[24:25], s[2:3]
	ml_and_b32 v20, tid, 0xf
	ml_add_i32 v1, v9, v4
	ml_shl_b32 v4, v8, 0x2
	ml_shl_b32 v1, v1, 0x2
	ml_addo_u32 {v9, tcr}, s2, v4
	ml_srl_b32 v4, v8, 0x1e
	ml_or_b32 v1, v1, v4
	ml_mov_b32 v4, s3
	ml_addc_i32 v1, v4, v1, tcr
	sl_shl_b64 {s[2:3], wcr}, s[6:7], 0x2
	ml_addo_u32 {v4, tcr}, s2, v9
	ml_mov_b32 v5, s3
	ml_shl_b32 v8, v20, 0x2
	sl_shl_b64 {s[6:7], wcr}, s[16:17], 0x4
	ml_addc_i32 v5, v1, v5, tcr
	ml_addo_u32 {v4, tcr}, v8, v4
	sl_add_i64 s[2:3], s[2:3], s[6:7]
	ml_mov_b32 v12, s3
	sl_mov_b32 s1, 0x40
	ml_addc_i32 v5, 0, v5, tcr
	ml_addo_u32 {v9, tcr}, s2, v9
	ml_lsa_store_a64_dword  v[4:5], v18, kop=0
	sl_mov_b32 s9, 0x0
	ml_addc_i32 v1, v12, v1, tcr
	ml_addo_u32 {v8, tcr}, v8, v9
	ml_addc_i32 v9, 0, v1, tcr
	ml_addo_u32 {v12, tcr}, s1, v4
	ml_lsa_store_a64_dword  v[8:9], v19, kop=0
	ml_addc_i32 v13, 0, v5, tcr
	ml_addo_u32 {v16, tcr}, s1, v8
	ml_lsa_store_a64_dword  v[12:13], v30, kop=0
	sl_mov_b32 s1, 0x80
	ml_addc_i32 v17, 0, v9, tcr
	ml_addo_u32 {v12, tcr}, s1, v4
	ml_lsa_store_a64_dword  v[16:17], v31, kop=0
	ml_addc_i32 v13, 0, v5, tcr
	ml_addo_u32 {v16, tcr}, s1, v8
	ml_lsa_store_a64_dword  v[12:13], v26, kop=0
	sl_mov_b32 s1, 0xc0
	ml_addc_i32 v17, 0, v9, tcr
	ml_addo_u32 {v12, tcr}, s1, v4
	ml_lsa_store_a64_dword  v[16:17], v27, kop=0
	ml_addc_i32 v13, 0, v5, tcr
	ml_addo_u32 {v16, tcr}, s1, v8
	ml_lsa_store_a64_dword  v[12:13], v22, kop=0
	sl_mov_b32 s1, 0x100
	ml_addc_i32 v17, 0, v9, tcr
	ml_addo_u32 {v12, tcr}, s1, v4
	ml_lsa_store_a64_dword  v[16:17], v23, kop=0
	ml_addc_i32 v13, 0, v5, tcr
	ml_addo_u32 {v16, tcr}, s1, v8
	ml_lsa_store_a64_dword  v[12:13], v14, kop=0
	sl_mov_b32 s1, 0x140
	ml_addc_i32 v17, 0, v9, tcr
	ml_addo_u32 {v12, tcr}, s1, v4
	ml_lsa_store_a64_dword  v[16:17], v15, kop=0
	ml_addc_i32 v13, 0, v5, tcr
	ml_addo_u32 {v14, tcr}, s1, v8
	ml_lsa_store_a64_dword  v[12:13], v10, kop=0
	sl_mov_b32 s1, 0x180
	ml_addc_i32 v15, 0, v9, tcr
	ml_addo_u32 {v10, tcr}, s1, v4
	ml_lsa_store_a64_dword  v[14:15], v11, kop=0
	ml_addc_i32 v11, 0, v5, tcr
	ml_addo_u32 {v12, tcr}, s1, v8
	sl_mov_b32 s1, 0x1c0
	ml_lsa_store_a64_dword  v[10:11], v6, kop=0
	ml_addc_i32 v13, 0, v9, tcr
	ml_addo_u32 {v4, tcr}, s1, v4
	ml_lsa_store_a64_dword  v[12:13], v7, kop=0
	ml_addc_i32 v5, 0, v5, tcr
	ml_addo_u32 {v1, tcr}, s1, v8
	ml_lsa_store_a64_dword  v[4:5], v2, kop=0
	ml_addc_i32 v2, 0, v9, tcr
	ml_lsa_store_a64_dword  v[1:2], v3, kop=0
	ml_cmp_eq_u32 tcr, v20, 0x0
	sl_and_savetmsk_b64 s[2:3], tcr, tmsk
	; mask branch BB0_30
	sl_cbr_tmskaz BB0_30
BB0_29:
	ml_mul_u64_u32 v[1:2], s22, v0
	sl_mull_u32 s6, s21, s0
	sl_mul_u64_u32 s[0:1], s20, s0
	sl_add_i32 s1, s1, s6
	ml_mul_u64_u32 v[3:4], s23, v0
	sl_add_i64 s[0:1], s[0:1], s[8:9]
	sl_lsa_load_b32x16 s[28:43], s[4:5], noreg, #128, ca
	ml_addo_u32 {v1, tcr}, s0, v1
	ml_shl_b32 v4, v1, 0x2
	ml_add_i32 v0, v2, v3
	ml_mov_b32 v2, s1
	ml_addc_i32 v0, v2, v0, tcr
	ml_shl_b32 v2, v0, 0x2
	ml_addo_u32 {v0, tcr}, s26, v4
	ml_srl_b32 v1, v1, 0x1e
	ml_or_b32 v5, v2, v1
	ml_mov_b32 v1, s27
	ml_addc_i32 v1, v1, v5, tcr
	sl_shl_b64 {s[0:1], wcr}, s[22:23], 0x4
	ml_addo_u32 {v2, tcr}, s0, v0
	ml_mul_f32 v3, v53, 0x3f317218
	ml_lsa_store_a64_dword  v[0:1], v3, kop=0
	ml_mov_b32 v6, s1
	ml_addc_i32 v3, v1, v6, tcr
	sl_wait smcnt(0)
	ml_addo_u32 {v0, tcr}, s28, v4
	ml_mul_f32 v1, v54, 0x3f317218
	ml_lsa_store_a64_dword  v[2:3], v1, kop=0
	ml_mov_b32 v1, s29
	ml_addc_i32 v1, v1, v5, tcr
	ml_addo_u32 {v2, tcr}, s0, v0
	ml_lsa_store_a64_dword  v[0:1], v50, kop=0
	ml_addc_i32 v3, v1, v6, tcr
	ml_lsa_store_a64_dword  v[2:3], v51, kop=0
BB0_30:
	sl_or_b64 {tmsk, wcr}, tmsk, s[2:3]
BB0_31:
	sl_eop 
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_.kd
	.type	_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_.kd,@object
	.size	_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_.kd, 64
_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_.kd:
	.asciz	"\000 \000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_@rel64-_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	537042
	.asciz	"#\000\364\006\211\000\000\000\000\000\000"
	.section	.text._Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_,"axG",@progbits,_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_,comdat
.Lfunc_end0:
	.size	_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_, .Lfunc_end0-_Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 7224
; NumSgprs: 62
; NumVgprs: 76
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 8192 bytes/workgroup (compile time only)
; SGPRBlocks: 7
; VGPRBlocks: 18
; NumSGPRsForWarpsPerNU: 58
; NumVGPRsForWarpsPerNR: 76
; ReqNTIDx: 0
; MaxNTIDx: 0
; MinCTASm: 1
; ActiveWarp: 3
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
      - .address_space:  global
        .name:           KArg_4
        .offset:         32
        .size:           8
        .value_kind:     global_buffer
      - .name:           KArg_5
        .offset:         40
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_6
        .offset:         48
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_7
        .offset:         56
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_8
        .offset:         64
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_9
        .offset:         72
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_10
        .offset:         80
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_11
        .offset:         88
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_12
        .offset:         96
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_13
        .offset:         104
        .size:           8
        .value_kind:     by_value
      - .address_space:  global
        .name:           KArg_14
        .offset:         112
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_15
        .offset:         120
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_16
        .offset:         128
        .size:           8
        .value_kind:     global_buffer
    .group_segment_fixed_size: 8192
    .kernarg_segment_align: 8
    .kernarg_segment_size: 136
    .max_flat_workgroup_size: 0
    .name:           _Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_
    .private_segment_fixed_size: 0
    .sgpr_count:     62
    .sgpr_spill_count: 0
    .symbol:         _Z31corex_native_gqa_producer_draftILj4EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_.kd
    .vgpr_count:     76
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
