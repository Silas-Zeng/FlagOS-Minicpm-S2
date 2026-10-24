	.text
	.globl	kernel_unified_attention        ; -- Begin function kernel_unified_attention
	.p2align	3
	.type	kernel_unified_attention,@function
	.iluvatar_kernel kernel_unified_attention
kernel_unified_attention:               ; @kernel_unified_attention
.Lfunc_begin0:
	.file	1 "/workspace/experiments/minicpm-s2/framework/20261022T121701Z-prefill-v-late-gate/source" "generated_attention.py"
	.loc	1 179 0                         ; generated_attention.py:179:0
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
		granulated_warp_sgpr_count = 12
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
		kernarg_segment_byte_size = 296
		workgroup_fbarrier_count = 0
		warp_sgpr_count = 104
		workitem_vgpr_count = 100
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
	sl_mul_u64_u32 s[10:11], s8, s2
	sl_shl_b64 {s[10:11], wcr}, s[10:11], 0x6
	sl_add_u64 s[0:1], s[0:1], s[10:11]
	sl_mov_b32 s2, 0xffffffff
	sl_mov_b64 s[98:99], s[2:3]
	sl_mov_b64 s[96:97], s[0:1]
	sl_mov_b32 s14, tcr_lo
	ml_vrf_init_u32 v48, tcr
.Ltmp0:
	.loc	1 288 39 prologue_end           ; generated_attention.py:288:39
	sl_lsa_load_b32x16 s[56:71], s[4:5], noreg, #128, ca
	sl_mov_b32 s2, 0x0
.Ltmp1:
	.file	2 "/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops" "triton_attention_helpers.py"
	.loc	2 96 17                         ; triton_attention_helpers.py:96:17 @[ triton_attention_helpers.py:67:68 @[ generated_attention.py:299:73 ] ]
	sl_wait smcnt(0)
	sl_cmp_gt_i32 wcr, s70, 0x0
	sl_cbr_wcrz BB0_3, wcr
; %bb.1:                                ; %.lr.ph.preheader
	.loc	2 0 17 is_stmt 0                ; triton_attention_helpers.py:0:17
	sl_mov_b32 s3, 0xffffffff
BB0_2:                                  ; %.lr.ph
                                        ; =>This Inner Loop Header: Depth=1
	.loc	2 97 22 is_stmt 1               ; triton_attention_helpers.py:97:22 @[ triton_attention_helpers.py:67:68 @[ generated_attention.py:299:73 ] ]
	sl_add_i32 s0, s2, s70
	.loc	2 97 32 is_stmt 0               ; triton_attention_helpers.py:97:32 @[ triton_attention_helpers.py:67:68 @[ generated_attention.py:299:73 ] ]
	sl_srl_b32 {s1, wcr}, s0, 0x1f
	sl_add_i32 s0, s0, s1
	sl_sra_b32 {s8, wcr}, s0, 0x1
	.loc	2 98 44 is_stmt 1               ; triton_attention_helpers.py:98:44 @[ triton_attention_helpers.py:67:68 @[ generated_attention.py:299:73 ] ]
	sl_sra_b32 {s9, wcr}, s8, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[8:9], 0x2
	sl_add_i64 s[0:1], s[68:69], s[0:1]
	.loc	2 98 22 is_stmt 0               ; triton_attention_helpers.py:98:22 @[ triton_attention_helpers.py:67:68 @[ generated_attention.py:299:73 ] ]
	ml_lsa_load_dword v0, s[0:3], noreg, noreg, #0, ca
	.loc	2 101 11 is_stmt 1              ; triton_attention_helpers.py:101:11 @[ triton_attention_helpers.py:67:68 @[ generated_attention.py:299:73 ] ]
	sl_add_i32 s1, s8, 0x1
	.loc	2 98 22                         ; triton_attention_helpers.py:98:22 @[ triton_attention_helpers.py:67:68 @[ generated_attention.py:299:73 ] ]
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s0, v0, 0x0
	.loc	2 99 25                         ; triton_attention_helpers.py:99:25 @[ triton_attention_helpers.py:67:68 @[ generated_attention.py:299:73 ] ]
	sl_sra_b32 {s9, wcr}, s0, 0x1f
	sl_srl_b32 {s9, wcr}, s9, 0x1c
	sl_add_i32 s0, s0, s9
	sl_sra_b32 {s0, wcr}, s0, 0x4
	.loc	2 99 35 is_stmt 0               ; triton_attention_helpers.py:99:35 @[ triton_attention_helpers.py:67:68 @[ generated_attention.py:299:73 ] ]
	sl_add_i32 s0, s0, s8
	.loc	2 101 22 is_stmt 1              ; triton_attention_helpers.py:101:22 @[ triton_attention_helpers.py:67:68 @[ generated_attention.py:299:73 ] ]
	sl_cmp_gt_i32 wcr, s0, s6
	.loc	2 101 11 is_stmt 0              ; triton_attention_helpers.py:101:11 @[ triton_attention_helpers.py:67:68 @[ generated_attention.py:299:73 ] ]
	sl_csel_b32 s70, s8, s70, wcr
	sl_csel_b32 s2, s2, s1, wcr
	.loc	2 96 17 is_stmt 1               ; triton_attention_helpers.py:96:17 @[ triton_attention_helpers.py:67:68 @[ generated_attention.py:299:73 ] ]
	sl_cmp_lt_i32 wcr, s2, s70
	sl_cbr_wcrnz BB0_2, wcr
BB0_3:                                  ; %._crit_edge
	.loc	2 106 18                        ; triton_attention_helpers.py:106:18 @[ triton_attention_helpers.py:67:68 @[ generated_attention.py:299:73 ] ]
	sl_add_i32 s8, s2, 0xffffffff
.Ltmp2:
	.loc	2 69 54                         ; triton_attention_helpers.py:69:54 @[ generated_attention.py:299:73 ]
	sl_sra_b32 {s9, wcr}, s8, 0x1f
	sl_mov_b32 s3, 0xffffffff
	sl_shl_b64 {s[12:13], wcr}, s[8:9], 0x2
	sl_add_i64 s[0:1], s[68:69], s[12:13]
	.loc	2 69 32 is_stmt 0               ; triton_attention_helpers.py:69:32 @[ generated_attention.py:299:73 ]
	ml_lsa_load_dwordx2 v[0:1], s[0:3], noreg, noreg, #0, ca
	.loc	2 69 76                         ; triton_attention_helpers.py:69:76 @[ generated_attention.py:299:73 ]
	sl_sub_i32 s0, s6, s2
	.loc	2 69 32                         ; triton_attention_helpers.py:69:32 @[ generated_attention.py:299:73 ]
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s42, v0, 0x0
	.loc	2 72 23 is_stmt 1               ; triton_attention_helpers.py:72:23 @[ generated_attention.py:299:73 ]
	ml_mov_v2s_b32 s1, v1, 0x0
	.loc	2 69 66                         ; triton_attention_helpers.py:69:66 @[ generated_attention.py:299:73 ]
	sl_sra_b32 {s2, wcr}, s42, 0x1f
	sl_srl_b32 {s2, wcr}, s2, 0x1c
	sl_add_i32 s2, s42, s2
	sl_srl_b32 {s2, wcr}, s2, 0x4
	.loc	2 69 76 is_stmt 0               ; triton_attention_helpers.py:69:76 @[ generated_attention.py:299:73 ]
	sl_sub_i32 s0, s0, s2
	.loc	2 70 45 is_stmt 1               ; triton_attention_helpers.py:70:45 @[ generated_attention.py:299:73 ]
	sl_mull_u32 s2, s0, 0x10
	.loc	2 73 37                         ; triton_attention_helpers.py:73:37 @[ generated_attention.py:299:73 ]
	sl_sub_i32 s15, s1, s42
.Ltmp3:
	.loc	1 302 27                        ; generated_attention.py:302:27
	sl_add_i32 s16, s2, 0x10
	.loc	1 302 38 is_stmt 0              ; generated_attention.py:302:38
	sl_cmp_lt_i32 wcr, s16, s15
	sl_cbr_wcrz BB0_88, wcr
; %bb.4:
	.loc	1 0 38                          ; generated_attention.py:0:38
	sl_lsa_load_b32x16 s[24:39], s[4:5], noreg, #0, ca
	sl_lsa_load_b32x16 s[68:83], s[4:5], noreg, #64, ca
	.loc	1 318 26 is_stmt 1              ; generated_attention.py:318:26
	sl_and_b32 {s6, wcr}, s14, 0x1c0
	sl_wait smcnt(0)
	sl_bfe2_b32 s38, s14, 0x66
	.loc	1 324 35                        ; generated_attention.py:324:35
	sl_mull_u32 s37, s7, 0x8
	ml_mov_b32 v49, 0x0
	ml_mov_b32 v12, 0x0
	ml_mov_b32 v10, 0x0
	ml_mov_b32 v8, 0x0
	ml_mov_b32 v6, 0x0
	ml_mov_b32 v4, 0x0
	ml_mov_b32 v2, 0x0
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i64 s[0:1], s[34:35], s[12:13]
	ml_lsa_load_dword v16, s[0:3], noreg, noreg, #0, ca
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v15, 0x0
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v3, 0x0
	ml_mov_b32 v5, 0x0
	ml_mov_b32 v7, 0x0
	ml_mov_b32 v9, 0x0
	ml_mov_b32 v11, 0x0
	ml_mov_b32 v13, 0x0
	ml_mov_b32 v14, 0x0
	.loc	1 333 45 is_stmt 1              ; generated_attention.py:333:45
	sl_cmp_lt_u32 wcr, s7, 0x2
	sl_sub_bi_u64 s[12:13], s[10:11], s[10:11], wcr
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s17, v16, 0x0
	.loc	1 353 12 is_stmt 1              ; generated_attention.py:353:12
	sl_cbr_wcrz BB0_35, wcr
; %bb.5:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s0, s2, 0x11
	sl_add_i32 s18, s2, 0x12
	sl_add_i32 s1, s38, s37
	sl_mull_u32 s3, s77, s1
	sl_mul_u64_u32 s[4:5], s76, s1
	sl_add_i32 s5, s5, s3
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x1
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s0, s15
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s3, 0xfff00004
	sl_cbr_wcrz BB0_7, wcr
; %bb.6:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s19, s0, s42
	sl_sra_b32 {s0, wcr}, s19, 0x1f
	sl_mull_u32 s20, s74, s0
	sl_mul_u64_u32 s[0:1], s74, s19
	sl_add_i32 s1, s1, s20
	sl_mull_u32 s19, s75, s19
	sl_add_i32 s1, s1, s19
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[0:1], s[26:27], s[0:1]
	sl_add_i64 s[0:1], s[0:1], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	ml_lsa_blkload_x1 v1, s[0:3], noreg, noreg, #0, ca
BB0_7:
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s18, s15
	sl_sub_bi_u64 s[0:1], s[10:11], s[10:11], wcr
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {tcr, wcr}, s[12:13], s[0:1]
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s1, s2, 0x13
	.loc	1 353 12 is_stmt 1              ; generated_attention.py:353:12
	sl_cbr_tcraz BB0_9, tcr
; %bb.8:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s0, s18, s42
	sl_sra_b32 {s20, wcr}, s0, 0x1f
	sl_mul_u64_u32 s[18:19], s74, s0
	sl_mull_u32 s20, s74, s20
	sl_add_i32 s19, s19, s20
	sl_mull_u32 s0, s75, s0
	sl_add_i32 s19, s19, s0
	sl_shl_b64 {s[18:19], wcr}, s[18:19], 0x1
	sl_add_i64 s[18:19], s[26:27], s[18:19]
	sl_add_i64 s[20:21], s[18:19], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s23, 0xfff00004
	ml_lsa_blkload_x1 v0, s[20:23], noreg, noreg, #0, ca
BB0_9:
	.loc	1 0 0                           ; generated_attention.py:0
	sl_add_i32 s18, s16, s42
	sl_add_i32 s0, s2, 0x14
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s1, s15
	sl_sub_bi_u64 s[20:21], s[10:11], s[10:11], wcr
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {tcr, wcr}, s[12:13], s[20:21]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_cbr_tcraz BB0_11, tcr
; %bb.10:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s1, s1, s42
	sl_sra_b32 {s19, wcr}, s1, 0x1f
	sl_mul_u64_u32 s[20:21], s74, s1
	sl_mull_u32 s19, s74, s19
	sl_add_i32 s19, s21, s19
	sl_mull_u32 s1, s75, s1
	sl_add_i32 s21, s19, s1
	sl_shl_b64 {s[20:21], wcr}, s[20:21], 0x1
	sl_add_i64 s[20:21], s[26:27], s[20:21]
	sl_add_i64 s[20:21], s[20:21], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s23, 0xfff00004
	ml_lsa_blkload_x1 v3, s[20:23], noreg, noreg, #0, ca
BB0_11:
	.loc	1 0 0                           ; generated_attention.py:0
	sl_sra_b32 {s19, wcr}, s18, 0x1f
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s0, s15
	sl_sub_bi_u64 s[20:21], s[10:11], s[10:11], wcr
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {tcr, wcr}, s[12:13], s[20:21]
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s1, s2, 0x15
	.loc	1 353 12 is_stmt 1              ; generated_attention.py:353:12
	sl_cbr_tcraz BB0_13, tcr
; %bb.12:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s0, s0, s42
	sl_sra_b32 {s22, wcr}, s0, 0x1f
	sl_mul_u64_u32 s[20:21], s74, s0
	sl_mull_u32 s22, s74, s22
	sl_add_i32 s21, s21, s22
	sl_mull_u32 s0, s75, s0
	sl_add_i32 s21, s21, s0
	sl_shl_b64 {s[20:21], wcr}, s[20:21], 0x1
	sl_add_i64 s[20:21], s[26:27], s[20:21]
	sl_add_i64 s[20:21], s[20:21], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s23, 0xfff00004
	ml_lsa_blkload_x1 v2, s[20:23], noreg, noreg, #0, ca
BB0_13:
	.loc	1 0 0                           ; generated_attention.py:0
	sl_add_i32 s20, s2, 0x16
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s1, s15
	sl_sub_bi_u64 s[22:23], s[10:11], s[10:11], wcr
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {tcr, wcr}, s[12:13], s[22:23]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_cbr_tcraz BB0_15, tcr
; %bb.14:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s21, s1, s42
	sl_sra_b32 {s22, wcr}, s21, 0x1f
	sl_mul_u64_u32 s[0:1], s74, s21
	sl_mull_u32 s22, s74, s22
	sl_add_i32 s1, s1, s22
	sl_mull_u32 s21, s75, s21
	sl_add_i32 s1, s1, s21
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[0:1], s[26:27], s[0:1]
	sl_add_i64 s[40:41], s[0:1], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s43, 0xfff00004
	ml_lsa_blkload_x1 v5, s[40:43], noreg, noreg, #0, ca
BB0_15:
	.loc	1 0 0                           ; generated_attention.py:0
	sl_add_i32 s21, s2, 0x17
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s20, s15
	sl_sub_bi_u64 s[0:1], s[10:11], s[10:11], wcr
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {tcr, wcr}, s[12:13], s[0:1]
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_mul_u64_u32 s[0:1], s74, s18
	.loc	1 353 12 is_stmt 1              ; generated_attention.py:353:12
	sl_cbr_tcraz BB0_17, tcr
; %bb.16:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s20, s20, s42
	sl_sra_b32 {s34, wcr}, s20, 0x1f
	sl_mul_u64_u32 s[22:23], s74, s20
	sl_mull_u32 s34, s74, s34
	sl_add_i32 s23, s23, s34
	sl_mull_u32 s20, s75, s20
	sl_add_i32 s23, s23, s20
	sl_shl_b64 {s[22:23], wcr}, s[22:23], 0x1
	sl_add_i64 s[22:23], s[26:27], s[22:23]
	sl_add_i64 s[40:41], s[22:23], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s43, 0xfff00004
	ml_lsa_blkload_x1 v4, s[40:43], noreg, noreg, #0, ca
BB0_17:
	.loc	1 0 0                           ; generated_attention.py:0
	sl_add_i32 s20, s2, 0x18
	sl_mull_u32 s22, s74, s19
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s21, s15
	sl_sub_bi_u64 s[34:35], s[10:11], s[10:11], wcr
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {tcr, wcr}, s[12:13], s[34:35]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_cbr_tcraz BB0_19, tcr
; %bb.18:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s19, s21, s42
	sl_sra_b32 {s21, wcr}, s19, 0x1f
	sl_mul_u64_u32 s[34:35], s74, s19
	sl_mull_u32 s21, s74, s21
	sl_add_i32 s21, s35, s21
	sl_mull_u32 s19, s75, s19
	sl_add_i32 s35, s21, s19
	sl_shl_b64 {s[34:35], wcr}, s[34:35], 0x1
	sl_add_i64 s[34:35], s[26:27], s[34:35]
	sl_add_i64 s[40:41], s[34:35], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s43, 0xfff00004
	ml_lsa_blkload_x1 v7, s[40:43], noreg, noreg, #0, ca
BB0_19:
	.loc	1 0 0                           ; generated_attention.py:0
	sl_add_i32 s19, s2, 0x19
	sl_add_i32 s1, s1, s22
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s20, s15
	sl_sub_bi_u64 s[22:23], s[10:11], s[10:11], wcr
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {tcr, wcr}, s[12:13], s[22:23]
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_mull_u32 s21, s75, s18
	.loc	1 353 12 is_stmt 1              ; generated_attention.py:353:12
	sl_cbr_tcraz BB0_21, tcr
; %bb.20:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s18, s20, s42
	sl_sra_b32 {s20, wcr}, s18, 0x1f
	sl_mul_u64_u32 s[22:23], s74, s18
	sl_mull_u32 s20, s74, s20
	sl_add_i32 s20, s23, s20
	sl_mull_u32 s18, s75, s18
	sl_add_i32 s23, s20, s18
	sl_shl_b64 {s[22:23], wcr}, s[22:23], 0x1
	sl_add_i64 s[22:23], s[26:27], s[22:23]
	sl_add_i64 s[40:41], s[22:23], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s43, 0xfff00004
	ml_lsa_blkload_x1 v6, s[40:43], noreg, noreg, #0, ca
BB0_21:
	.loc	1 0 0                           ; generated_attention.py:0
	sl_add_i32 s18, s2, 0x1a
	sl_add_i32 s1, s1, s21
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s19, s15
	sl_sub_bi_u64 s[20:21], s[10:11], s[10:11], wcr
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {tcr, wcr}, s[12:13], s[20:21]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_cbr_tcraz BB0_23, tcr
; %bb.22:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s19, s19, s42
	sl_sra_b32 {s22, wcr}, s19, 0x1f
	sl_mul_u64_u32 s[20:21], s74, s19
	sl_mull_u32 s22, s74, s22
	sl_add_i32 s21, s21, s22
	sl_mull_u32 s19, s75, s19
	sl_add_i32 s21, s21, s19
	sl_shl_b64 {s[20:21], wcr}, s[20:21], 0x1
	sl_add_i64 s[20:21], s[26:27], s[20:21]
	sl_add_i64 s[20:21], s[20:21], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s23, 0xfff00004
	ml_lsa_blkload_x1 v9, s[20:23], noreg, noreg, #0, ca
BB0_23:
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s18, s15
	sl_sub_bi_u64 s[20:21], s[10:11], s[10:11], wcr
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {tcr, wcr}, s[12:13], s[20:21]
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s19, s2, 0x1b
	.loc	1 353 12 is_stmt 1              ; generated_attention.py:353:12
	sl_cbr_tcraz BB0_25, tcr
; %bb.24:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s18, s18, s42
	sl_sra_b32 {s22, wcr}, s18, 0x1f
	sl_mul_u64_u32 s[20:21], s74, s18
	sl_mull_u32 s22, s74, s22
	sl_add_i32 s21, s21, s22
	sl_mull_u32 s18, s75, s18
	sl_add_i32 s21, s21, s18
	sl_shl_b64 {s[20:21], wcr}, s[20:21], 0x1
	sl_add_i64 s[20:21], s[26:27], s[20:21]
	sl_add_i64 s[20:21], s[20:21], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s23, 0xfff00004
	ml_lsa_blkload_x1 v8, s[20:23], noreg, noreg, #0, ca
BB0_25:
	.loc	1 0 0                           ; generated_attention.py:0
	sl_add_i32 s18, s2, 0x1c
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s19, s15
	sl_sub_bi_u64 s[20:21], s[10:11], s[10:11], wcr
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {tcr, wcr}, s[12:13], s[20:21]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_cbr_tcraz BB0_27, tcr
; %bb.26:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s19, s19, s42
	sl_sra_b32 {s22, wcr}, s19, 0x1f
	sl_mul_u64_u32 s[20:21], s74, s19
	sl_mull_u32 s22, s74, s22
	sl_add_i32 s21, s21, s22
	sl_mull_u32 s19, s75, s19
	sl_add_i32 s21, s21, s19
	sl_shl_b64 {s[20:21], wcr}, s[20:21], 0x1
	sl_add_i64 s[20:21], s[26:27], s[20:21]
	sl_add_i64 s[20:21], s[20:21], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s23, 0xfff00004
	ml_lsa_blkload_x1 v11, s[20:23], noreg, noreg, #0, ca
BB0_27:
	.loc	1 0 0                           ; generated_attention.py:0
	sl_add_i32 s19, s2, 0x1d
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s18, s15
	sl_sub_bi_u64 s[20:21], s[10:11], s[10:11], wcr
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {tcr, wcr}, s[12:13], s[20:21]
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i64 s[0:1], s[26:27], s[0:1]
	.loc	1 353 12 is_stmt 1              ; generated_attention.py:353:12
	sl_cbr_tcraz BB0_29, tcr
; %bb.28:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s18, s18, s42
	sl_sra_b32 {s22, wcr}, s18, 0x1f
	sl_mul_u64_u32 s[20:21], s74, s18
	sl_mull_u32 s22, s74, s22
	sl_add_i32 s21, s21, s22
	sl_mull_u32 s18, s75, s18
	sl_add_i32 s21, s21, s18
	sl_shl_b64 {s[20:21], wcr}, s[20:21], 0x1
	sl_add_i64 s[20:21], s[26:27], s[20:21]
	sl_add_i64 s[20:21], s[20:21], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s23, 0xfff00004
	ml_lsa_blkload_x1 v10, s[20:23], noreg, noreg, #0, ca
BB0_29:
	.loc	1 0 0                           ; generated_attention.py:0
	sl_add_i32 s18, s2, 0x1e
	sl_add_i64 s[0:1], s[0:1], s[4:5]
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s19, s15
	sl_sub_bi_u64 s[20:21], s[10:11], s[10:11], wcr
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {tcr, wcr}, s[12:13], s[20:21]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_cbr_tcraz BB0_31, tcr
; %bb.30:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s19, s19, s42
	sl_sra_b32 {s22, wcr}, s19, 0x1f
	sl_mul_u64_u32 s[20:21], s74, s19
	sl_mull_u32 s22, s74, s22
	sl_add_i32 s21, s21, s22
	sl_mull_u32 s19, s75, s19
	sl_add_i32 s21, s21, s19
	sl_shl_b64 {s[20:21], wcr}, s[20:21], 0x1
	sl_add_i64 s[20:21], s[26:27], s[20:21]
	sl_add_i64 s[20:21], s[20:21], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s23, 0xfff00004
	ml_lsa_blkload_x1 v13, s[20:23], noreg, noreg, #0, ca
BB0_31:
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s18, s15
	sl_sub_bi_u64 s[20:21], s[10:11], s[10:11], wcr
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {tcr, wcr}, s[12:13], s[20:21]
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s2, s2, 0x1f
	.loc	1 353 12 is_stmt 1              ; generated_attention.py:353:12
	sl_cbr_tcraz BB0_33, tcr
; %bb.32:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s20, s18, s42
	sl_sra_b32 {s21, wcr}, s20, 0x1f
	sl_mul_u64_u32 s[18:19], s74, s20
	sl_mull_u32 s21, s74, s21
	sl_add_i32 s19, s19, s21
	sl_mull_u32 s20, s75, s20
	sl_add_i32 s19, s19, s20
	sl_shl_b64 {s[18:19], wcr}, s[18:19], 0x1
	sl_add_i64 s[18:19], s[26:27], s[18:19]
	sl_add_i64 s[20:21], s[18:19], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s23, 0xfff00004
	ml_lsa_blkload_x1 v12, s[20:23], noreg, noreg, #0, ca
BB0_33:
	.loc	1 0 0                           ; generated_attention.py:0
	ml_lsa_blkload_x1 v15, s[0:3], noreg, noreg, #0, ca
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s2, s15
	sl_sub_bi_u64 s[0:1], s[10:11], s[10:11], wcr
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {tcr, wcr}, s[12:13], s[0:1]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_cbr_tcraz BB0_35, tcr
; %bb.34:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s2, s2, s42
	sl_sra_b32 {s3, wcr}, s2, 0x1f
	sl_mul_u64_u32 s[0:1], s74, s2
	sl_mull_u32 s3, s74, s3
	sl_add_i32 s1, s1, s3
	sl_mull_u32 s2, s75, s2
	sl_add_i32 s1, s1, s2
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[0:1], s[26:27], s[0:1]
	sl_add_i64 s[0:1], s[0:1], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_mov_b32 s3, 0xfff00004
	ml_lsa_blkload_x1 v14, s[0:3], noreg, noreg, #0, ca
BB0_35:                                 ; %.thread34
	.loc	1 318 26 is_stmt 1              ; generated_attention.py:318:26
	ml_and_b32 v16, tid, 0x30
	.loc	1 321 56                        ; generated_attention.py:321:56
	sl_srl_b32 {s0, wcr}, s6, 0x5
	.loc	1 321 46 is_stmt 0              ; generated_attention.py:321:46
	sl_add_i32 s20, s16, s0
	sl_add_i32 s19, s20, 0x1
	.loc	1 332 40 is_stmt 1              ; generated_attention.py:332:40
	sl_cmp_lt_i32 wcr, s20, s15
	sl_sub_bi_u64 s[0:1], s[10:11], s[10:11], wcr
	sl_cmp_lt_i32 wcr, s19, s15
	sl_sub_bi_u64 s[4:5], s[10:11], s[10:11], wcr
	.loc	1 353 12                        ; generated_attention.py:353:12
	ml_shl_b32 v16, v16, 0x6
	ml_shl_b32 v17, v48, 0x3
	sl_srl_b32 {s2, wcr}, s14, 0x1
	sl_and_b32 {s2, wcr}, s2, 0xc0
	ml_and_b32 v18, tid, 0x8
	ml_cmp_eq_u32 tcr, v18, 0x0
	ml_mov_b32 v18, 0x280
	ml_csel_b32 v18, 0, v18, tcr
	sl_srl_b32 {s3, wcr}, s14, 0x5
	sl_and_b32 {s3, wcr}, s3, 0x2
	ml_anyop3_b32 v16, v16, v17, 56, 0xffffffea
	ml_xor_b32 v17, s2, v18
	ml_anyop3_b32 v55, v17, v16, s3, 0xfffffffe
	sl_wait vmcnt(0)
	ml_slb_store_b16  v15, v55, noreg, #0, null
	ml_srl_b32 v15, v15, 0x10
	sl_mov_b32 s2, 0x1000
	.loc	1 318 26                        ; generated_attention.py:318:26
	ml_and_b32 v58, tid, 0xf
	.loc	1 353 12                        ; generated_attention.py:353:12
	ml_slb_store_b16  v15, v55, noreg, #4, null
	sl_mov_b32 s18, 0x7000
	ml_slb_store_b16  v1, v55, noreg, #256, null
	ml_srl_b32 v1, v1, 0x10
	ml_slb_store_b16  v1, v55, noreg, #260, null
	ml_srl_b32 v1, v14, 0x10
	ml_slb_store_b16  v0, v55, s2, #0, null
	ml_srl_b32 v0, v0, 0x10
	ml_slb_store_b16  v0, v55, s2, #4, null
	ml_srl_b32 v0, v3, 0x10
	ml_slb_store_b16  v3, v55, s2, #256, null
	ml_slb_store_b16  v0, v55, s2, #260, null
	sl_mov_b32 s2, 0x2000
	ml_srl_b32 v0, v2, 0x10
	ml_slb_store_b16  v2, v55, s2, #0, null
	ml_slb_store_b16  v0, v55, s2, #4, null
	ml_srl_b32 v0, v5, 0x10
	ml_slb_store_b16  v5, v55, s2, #256, null
	ml_slb_store_b16  v0, v55, s2, #260, null
	sl_mov_b32 s2, 0x3000
	ml_srl_b32 v0, v4, 0x10
	ml_slb_store_b16  v4, v55, s2, #0, null
	ml_slb_store_b16  v0, v55, s2, #4, null
	ml_srl_b32 v0, v7, 0x10
	ml_slb_store_b16  v7, v55, s2, #256, null
	ml_slb_store_b16  v0, v55, s2, #260, null
	sl_mov_b32 s2, 0x4000
	ml_srl_b32 v0, v6, 0x10
	ml_slb_store_b16  v6, v55, s2, #0, null
	ml_slb_store_b16  v0, v55, s2, #4, null
	ml_srl_b32 v0, v9, 0x10
	ml_slb_store_b16  v9, v55, s2, #256, null
	ml_slb_store_b16  v0, v55, s2, #260, null
	sl_mov_b32 s2, 0x5000
	ml_srl_b32 v0, v8, 0x10
	ml_slb_store_b16  v8, v55, s2, #0, null
	ml_slb_store_b16  v0, v55, s2, #4, null
	ml_srl_b32 v0, v11, 0x10
	ml_slb_store_b16  v11, v55, s2, #256, null
	ml_slb_store_b16  v0, v55, s2, #260, null
	sl_mov_b32 s2, 0x6000
	ml_srl_b32 v0, v10, 0x10
	ml_slb_store_b16  v10, v55, s2, #0, null
	ml_slb_store_b16  v0, v55, s2, #4, null
	ml_srl_b32 v0, v13, 0x10
	ml_slb_store_b16  v13, v55, s2, #256, null
	ml_slb_store_b16  v0, v55, s2, #260, null
	.loc	1 354 61                        ; generated_attention.py:354:61
	sl_and_b64 {s[2:3], wcr}, s[12:13], s[0:1]
	sl_and_b64 {s[0:1], wcr}, s[12:13], s[4:5]
	.loc	1 353 12                        ; generated_attention.py:353:12
	ml_srl_b32 v0, v12, 0x10
	ml_slb_store_b16  v12, v55, s18, #0, null
	.loc	1 372 28                        ; generated_attention.py:372:28
	sl_sub_i32 s4, s17, s15
.Ltmp4:
	.loc	2 181 10                        ; triton_attention_helpers.py:181:10 @[ generated_attention.py:399:8 ]
	sl_add_i32 s5, s16, s4
	.loc	2 183 10                        ; triton_attention_helpers.py:183:10 @[ generated_attention.py:399:8 ]
	sl_add_i32 s5, s5, 0x10
.Ltmp5:
	.loc	1 353 12                        ; generated_attention.py:353:12
	ml_slb_store_b16  v0, v55, s18, #4, null
.Ltmp6:
	.loc	2 191 60                        ; triton_attention_helpers.py:191:60 @[ generated_attention.py:399:8 ]
	sl_min_i32 s26, s5, s17
.Ltmp7:
	.loc	2 24 20                         ; triton_attention_helpers.py:24:20 @[ triton_attention_helpers.py:193:44 @[ generated_attention.py:399:8 ] ]
	sl_add_i32 s5, s26, 0x3f
.Ltmp8:
	.loc	1 403 28                        ; generated_attention.py:403:28
	sl_cmp_gt_i32 wcr, s5, 0x3f
	.loc	1 353 12                        ; generated_attention.py:353:12
	ml_slb_store_b16  v14, v55, s18, #256, null
	ml_slb_store_b16  v1, v55, s18, #260, null
	.loc	1 403 28                        ; generated_attention.py:403:28
	sl_cbr_wcrz BB0_70, wcr
; %bb.36:                               ; %.lr.ph62
	.loc	1 0 28 is_stmt 0                ; generated_attention.py:0:28
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v99, s98, 0x0
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v99, s98, 0x1
	sl_mov_b32 s98, 0xffffffff
	ml_mov_s2v_b32 v99, s37, 0x2
	ml_mov_s2v_b32 v99, s42, 0x3
	.loc	1 358 35 is_stmt 1              ; generated_attention.py:358:35
	sl_mull_u32 s9, s72, s9
	sl_mul_u64_u32 s[12:13], s72, s8
	sl_add_i32 s9, s13, s9
	ml_mov_s2v_b32 v99, s68, 0x4
	ml_mov_s2v_b32 v99, s69, 0x5
	ml_mov_s2v_b32 v99, s70, 0x6
	ml_mov_s2v_b32 v99, s71, 0x7
	ml_mov_s2v_b32 v99, s72, 0x8
	ml_mov_s2v_b32 v99, s73, 0x9
	ml_mov_s2v_b32 v99, s74, 0xa
	ml_mov_s2v_b32 v99, s75, 0xb
	ml_mov_s2v_b32 v99, s76, 0xc
	ml_mov_s2v_b32 v99, s77, 0xd
	ml_mov_s2v_b32 v99, s78, 0xe
	ml_mov_s2v_b32 v99, s79, 0xf
	ml_mov_s2v_b32 v99, s80, 0x10
	ml_mov_s2v_b32 v99, s81, 0x11
	ml_mov_s2v_b32 v99, s82, 0x12
	ml_mov_s2v_b32 v99, s83, 0x13
	sl_mull_u32 s8, s73, s8
	sl_add_i32 s13, s9, s8
	.loc	1 408 31                        ; generated_attention.py:408:31
	sl_shl_b64 {s[8:9], wcr}, s[12:13], 0x2
	sl_add_i64 s[32:33], s[32:33], s[8:9]
	.loc	1 460 32                        ; generated_attention.py:460:32
	sl_mull_u32 s12, s61, s7
	sl_mul_u64_u32 s[8:9], s60, s7
	sl_add_i32 s9, s9, s12
	.loc	1 548 32                        ; generated_attention.py:548:32
	sl_mull_u32 s15, s67, s7
	sl_mul_u64_u32 s[12:13], s66, s7
	sl_add_i32 s13, s13, s15
	.loc	1 403 28                        ; generated_attention.py:403:28
	sl_shl_b64 {s[8:9], wcr}, s[8:9], 0x1
	sl_add_i64 s[34:35], s[28:29], s[8:9]
	sl_mov_b32 s16, s38
	sl_mov_b32 s17, 0x0
	sl_shl_b64 {s[8:9], wcr}, s[12:13], 0x1
	sl_add_i64 s[40:41], s[30:31], s[8:9]
	ml_mov_s2v_b32 v99, s19, 0x14
	.loc	1 500 38                        ; generated_attention.py:500:38
	sl_add_i32 s30, s19, s4
	ml_mov_s2v_b32 v99, s20, 0x15
	sl_add_i32 s72, s20, s4
.Ltmp9:
	.loc	2 24 26                         ; triton_attention_helpers.py:24:26 @[ triton_attention_helpers.py:193:44 @[ generated_attention.py:399:8 ] ]
	sl_srl_b32 {s42, wcr}, s5, 0x6
	ml_shl_b32 v0, v48, 0x6
	ml_and_b32 v1, tid, 0xc
	ml_shl_b32 v2, v1, 0x2
	sl_srl_b32 {s4, wcr}, s14, 0x4
	sl_and_b32 {s4, wcr}, s4, 0xc
	sl_and_b32 {s5, wcr}, s14, 0x100
	sl_mov_b32 s5, 0x110
	sl_csel_b32 s5, s5, 0x0, wcr
	sl_mov_b32 s7, 0xcc0
	ml_anyop3_b32 v0, s7, v0, v2, 0xfffffff8
	sl_add_i32 s4, s5, s4
	ml_xor_b32 v60, s4, v0
	ml_xor_b32 v61, v60, 0x20
	sl_mull_u32 s73, s6, 0x40
	ml_shl_b32 v0, tid, 0x2
	ml_add_i32 v2, s73, v0
	ml_xor_b32 v62, v2, 0x80
	ml_shl_b32 v1, v1, 0x6
	ml_or_b32 v63, v1, v0
	ml_xor_b32 v64, v63, 0x10
	ml_xor_b32 v65, v63, 0x20
	ml_xor_b32 v66, v63, 0x30
	ml_xor_b32 v53, tid, 0x8
	ml_xor_b32 v52, tid, 0x4
	ml_xor_b32 v51, tid, 0x2
	ml_xor_b32 v50, tid, 0x1
	ml_and_b32 v1, tid, 0x10
	ml_cmp_eq_u32 tcr, v1, 0x0
	ml_mov_b32 v2, 0x5410
	ml_mov_b32 v3, 0x7632
	ml_csel_b32 v67, v2, v3, tcr
	ml_csel_b32 v68, v3, v2, tcr
	ml_shl_b32 v1, v1, 0x1
	ml_and_b32 v4, tid, 0x20
	ml_cmp_eq_u32 tcr, v4, 0x0
	ml_mov_b32 v5, 0x1054
	ml_csel_b32 v69, v2, v5, tcr
	ml_mov_b32 v2, 0x3276
	ml_csel_b32 v70, v3, v2, tcr
	ml_srl_b32 v2, v4, 0x1
.Ltmp10:
	.loc	1 318 26                        ; generated_attention.py:318:26
	ml_and_b32 v3, tid, 0xf
	ml_anyop3_b32 v71, v1, v2, v3, 0xfffffffe
	ml_xor_b32 v72, v71, 0x10
	ml_xor_b32 v73, v0, 0x80
	.loc	1 403 28                        ; generated_attention.py:403:28
	sl_add_i32 s4, s38, 0x8
	sl_mov_b32 s27, s17
	sl_sra_b32 {s74, wcr}, s30, 0x1f
	sl_sra_b32 {s75, wcr}, s72, 0x1f
	sl_mov_b32 s43, s17
	sl_mull_u32 s5, s59, s4
	sl_mul_u64_u32 s[44:45], s58, s4
	sl_add_i32 s45, s45, s5
	sl_mull_u32 s5, s59, s38
	sl_mul_u64_u32 s[46:47], s58, s38
	sl_add_i32 s47, s47, s5
	sl_mull_u32 s5, s65, s4
	sl_mul_u64_u32 s[48:49], s64, s4
	sl_add_i32 s49, s49, s5
	sl_mull_u32 s4, s65, s38
	sl_mov_b64 s[84:85], s[16:17]
	sl_mul_u64_u32 s[54:55], s64, s38
	sl_add_i32 s55, s55, s4
	sl_sub_u64 s[58:59], s[10:11], s[10:11]
	ml_mov_b32 v59, 0x0
	ml_mov_b32 v74, 0xff800000
	sl_mov_b32 s23, 0xffffffff
	sl_mov_b32 s31, 0xfff00004
	sl_mov_b32 s77, 0x1000504
	sl_mov_b32 s78, 0x2010200
	sl_mov_b32 s79, 0x8000
	sl_mov_b32 s80, 0x9000
	sl_mov_b32 s81, 0xa000
	sl_mov_b32 s82, 0xb000
	sl_mov_b32 s83, 0x800
	sl_mov_b32 s86, 0x8400
	sl_mov_b32 s87, 0x8800
	sl_mov_b32 s88, 0x8c00
	sl_mov_b32 s89, 0x9400
	sl_mov_b32 s90, 0x9800
	sl_mov_b32 s91, 0x9c00
	sl_mov_b32 s92, 0xa400
	sl_mov_b32 s93, 0xa800
	sl_mov_b32 s94, 0xac00
	sl_mov_b32 s37, 0xb400
	sl_mov_b32 s4, 0xb800
	sl_mov_b32 s5, 0xbc00
	ml_mov_b32 v57, 0x0
	ml_mov_b32 v56, 0x0
	ml_mov_b32 v54, 0x0
	ml_mov_b32 v24, 0x0
	ml_mov_b32 v25, 0x0
	ml_mov_b32 v26, 0x0
	ml_mov_b32 v27, 0x0
	ml_mov_b32 v28, 0x0
	ml_mov_b32 v29, 0x0
	ml_mov_b32 v30, 0x0
	ml_mov_b32 v31, 0x0
	ml_mov_b32 v16, 0x0
	ml_mov_b32 v17, 0x0
	ml_mov_b32 v18, 0x0
	ml_mov_b32 v19, 0x0
	ml_mov_b32 v20, 0x0
	ml_mov_b32 v21, 0x0
	ml_mov_b32 v22, 0x0
	ml_mov_b32 v23, 0x0
	ml_mov_b32 v8, 0x0
	ml_mov_b32 v9, 0x0
	ml_mov_b32 v10, 0x0
	ml_mov_b32 v11, 0x0
	ml_mov_b32 v12, 0x0
	ml_mov_b32 v13, 0x0
	ml_mov_b32 v14, 0x0
	ml_mov_b32 v15, 0x0
	ml_mov_b32 v4, 0x0
	ml_mov_b32 v5, 0x0
	ml_mov_b32 v6, 0x0
	ml_mov_b32 v7, 0x0
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v2, 0x0
	ml_mov_b32 v3, 0x0
	ml_mov_b32 v77, 0xff800000
	ml_mov_b32 v76, 0xff800000
	ml_mov_b32 v75, 0xff800000
	sl_jump BB0_38
BB0_37:                                 ;   in Loop: Header=BB0_38 Depth=1
.Ltmp11:
	.loc	2 406 24                        ; triton_attention_helpers.py:406:24 @[ generated_attention.py:543:44 ]
	ml_max_f32 v32, v77, v32
	ml_max_f32 v33, v76, v33
	ml_max_f32 v88, v75, v88
	ml_max_f32 v89, v74, v89
	.loc	2 409 25                        ; triton_attention_helpers.py:409:25 @[ generated_attention.py:543:44 ]
	ml_cmp_ne_f32 tcr, v32, 0xff800000
	.loc	2 409 45 is_stmt 0              ; triton_attention_helpers.py:409:45 @[ generated_attention.py:543:44 ]
	ml_csel_b32 v32, v32, v49, tcr
	.loc	2 409 25                        ; triton_attention_helpers.py:409:25 @[ generated_attention.py:543:44 ]
	ml_cmp_ne_f32 tcr, v33, 0xff800000
	.loc	2 409 45                        ; triton_attention_helpers.py:409:45 @[ generated_attention.py:543:44 ]
	ml_csel_b32 v33, v33, v49, tcr
	.loc	2 409 25                        ; triton_attention_helpers.py:409:25 @[ generated_attention.py:543:44 ]
	ml_cmp_ne_f32 tcr, v88, 0xff800000
	.loc	2 411 19 is_stmt 1              ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v34, v34, v32
	.loc	2 411 15 is_stmt 0              ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v90, v34, 0x3fb8aa3b
	.loc	2 409 45 is_stmt 1              ; triton_attention_helpers.py:409:45 @[ generated_attention.py:543:44 ]
	ml_csel_b32 v34, v88, v49, tcr
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v88, v90
	.loc	2 411 19 is_stmt 0              ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v87, v87, v33
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v87, v87, 0x3fb8aa3b
	.loc	2 409 25 is_stmt 1              ; triton_attention_helpers.py:409:25 @[ generated_attention.py:543:44 ]
	ml_cmp_ne_f32 tcr, v89, 0xff800000
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v87, v87
	.loc	2 411 19 is_stmt 0              ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v35, v35, v34
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v90, v35, 0x3fb8aa3b
	.loc	2 409 45 is_stmt 1              ; triton_attention_helpers.py:409:45 @[ generated_attention.py:543:44 ]
	ml_csel_b32 v35, v89, v49, tcr
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v89, v90
	.loc	2 411 19 is_stmt 0              ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v47, v47, v35
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v47, v47, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v86, v86, v32
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v47, v47
	ml_mul_f32 v86, v86, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v45, v45, v33
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v45, v45, 0x3fb8aa3b
	ml_exp_f32 v86, v86
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v46, v46, v34
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v46, v46, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v43, v43, v35
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v45, v45
	ml_mul_f32 v43, v43, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v44, v44, v32
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v44, v44, 0x3fb8aa3b
	ml_exp_f32 v46, v46
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v41, v41, v33
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v41, v41, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v42, v42, v34
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v43, v43
	ml_mul_f32 v42, v42, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v39, v39, v35
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v39, v39, 0x3fb8aa3b
	ml_exp_f32 v44, v44
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v40, v40, v32
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v40, v40, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v37, v37, v33
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v41, v41
	ml_mul_f32 v37, v37, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v38, v38, v34
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v38, v38, 0x3fb8aa3b
	ml_exp_f32 v42, v42
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v36, v36, v35
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v36, v36, 0x3fb8aa3b
	.loc	2 415 23 is_stmt 1              ; triton_attention_helpers.py:415:23 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v77, v77, v32
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v39, v39
	.loc	2 415 19                        ; triton_attention_helpers.py:415:19 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v77, v77, 0x3fb8aa3b
.Ltmp12:
	.file	3 "/usr/local/lib/python3.12/site-packages/triton/language" "standard.py"
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	ml_add_f32 v90, v88, v86
	ml_add_f32 v90, v44, v90
.Ltmp13:
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v40, v40
	.loc	2 415 23                        ; triton_attention_helpers.py:415:23 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v76, v76, v33
	.loc	2 415 19 is_stmt 0              ; triton_attention_helpers.py:415:19 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v76, v76, 0x3fb8aa3b
	.loc	2 415 23                        ; triton_attention_helpers.py:415:23 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v75, v75, v34
	.loc	2 411 15 is_stmt 1              ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v37, v37
	.loc	2 415 19                        ; triton_attention_helpers.py:415:19 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v75, v75, 0x3fb8aa3b
.Ltmp14:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	ml_add_f32 v90, v40, v90
.Ltmp15:
	.loc	2 415 23                        ; triton_attention_helpers.py:415:23 @[ generated_attention.py:543:44 ]
	ml_sub_f32 v74, v74, v35
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v38, v38
	.loc	2 415 19                        ; triton_attention_helpers.py:415:19 @[ generated_attention.py:543:44 ]
	ml_mul_f32 v74, v74, 0x3fb8aa3b
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v36, v36
	.loc	2 415 19                        ; triton_attention_helpers.py:415:19 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v77, v77
	ml_exp_f32 v76, v76
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ generated_attention.py:543:44 ]
	ml_fma_f32 v59, v59, v77, v90
.Ltmp16:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	ml_add_f32 v90, v87, v45
	ml_add_f32 v90, v41, v90
	ml_add_f32 v90, v37, v90
.Ltmp17:
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ generated_attention.py:543:44 ]
	ml_fma_f32 v57, v57, v76, v90
.Ltmp18:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	ml_add_f32 v90, v89, v46
.Ltmp19:
	.loc	2 415 19                        ; triton_attention_helpers.py:415:19 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v75, v75
.Ltmp20:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	ml_add_f32 v90, v42, v90
	ml_add_f32 v90, v38, v90
.Ltmp21:
	.loc	1 544 20                        ; generated_attention.py:544:20
	ml_mul_f32 v24, v24, v77
.Ltmp22:
	.loc	2 415 19                        ; triton_attention_helpers.py:415:19 @[ generated_attention.py:543:44 ]
	ml_exp_f32 v74, v74
.Ltmp23:
	.loc	1 544 20                        ; generated_attention.py:544:20
	ml_mul_f32 v28, v28, v77
.Ltmp24:
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ generated_attention.py:543:44 ]
	ml_fma_f32 v56, v56, v75, v90
.Ltmp25:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	ml_add_f32 v90, v47, v43
	ml_add_f32 v90, v39, v90
	ml_add_f32 v90, v36, v90
.Ltmp26:
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ generated_attention.py:543:44 ]
	ml_fma_f32 v54, v54, v74, v90
.Ltmp27:
	.loc	1 544 20                        ; generated_attention.py:544:20
	ml_mul_f32 v16, v16, v77
	ml_mul_f32 v20, v20, v77
	ml_mul_f32 v8, v8, v77
	ml_mul_f32 v12, v12, v77
	ml_mul_f32 v4, v4, v77
	ml_mul_f32 v0, v0, v77
	ml_mul_f32 v25, v25, v76
	ml_mul_f32 v29, v29, v76
	ml_mul_f32 v17, v17, v76
	ml_mul_f32 v21, v21, v76
	ml_mul_f32 v9, v9, v76
	ml_mul_f32 v13, v13, v76
	ml_mul_f32 v5, v5, v76
	ml_mul_f32 v1, v1, v76
	ml_mul_f32 v26, v26, v75
	ml_mul_f32 v30, v30, v75
	ml_mul_f32 v18, v18, v75
	ml_mul_f32 v22, v22, v75
	ml_mul_f32 v10, v10, v75
	ml_mul_f32 v14, v14, v75
	ml_mul_f32 v6, v6, v75
	ml_mul_f32 v2, v2, v75
	ml_mul_f32 v27, v27, v74
	ml_mul_f32 v31, v31, v74
	ml_mul_f32 v19, v19, v74
	ml_mul_f32 v23, v23, v74
	ml_mul_f32 v11, v11, v74
	ml_mul_f32 v15, v15, v74
	ml_mul_f32 v7, v7, v74
	ml_mul_f32 v3, v3, v74
	.loc	1 553 16                        ; generated_attention.py:553:16
	sl_wait vmcnt(0)
	sl_barrier 
	ml_slb_store_b16  v79, v55, s79, #0, null
	ml_srl_b32 v74, v79, 0x10
	ml_srl_b32 v75, v81, 0x10
	ml_srl_b32 v76, v85, 0x10
	ml_slb_store_b16  v74, v55, s79, #4, null
	ml_srl_b32 v74, v78, 0x10
	ml_srl_b32 v77, v82, 0x10
	.loc	1 579 31                        ; generated_attention.py:579:31
	ml_cvt_bf16_f32  v79, v87
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_store_b16  v78, v55, s79, #256, null
	.loc	1 579 31                        ; generated_attention.py:579:31
	ml_cvt_bf16_f32  v78, v88
	ml_cvt_bf16_f32  v47, v47
	ml_cvt_bf16_f32  v45, v45
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_store_b16  v74, v55, s79, #260, null
	ml_srl_b32 v74, v83, 0x10
	.loc	1 579 31                        ; generated_attention.py:579:31
	ml_cvt_bf16_f32  v46, v46
	ml_cvt_bf16_f32  v43, v43
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_store_b16  v83, v55, s80, #0, null
	.loc	1 579 31                        ; generated_attention.py:579:31
	ml_cvt_bf16_f32  v44, v44
	ml_cvt_bf16_f32  v41, v41
	ml_cvt_bf16_f32  v42, v42
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_store_b16  v74, v55, s80, #4, null
	ml_srl_b32 v74, v84, 0x10
	.loc	1 579 31                        ; generated_attention.py:579:31
	ml_cvt_bf16_f32  v39, v39
	ml_byte_permute_b32 v43, v43, v46, s77
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_store_b16  v81, v55, s80, #256, null
	.loc	1 579 31                        ; generated_attention.py:579:31
	ml_cvt_bf16_f32  v81, v89
	ml_byte_permute_b32 v47, v47, v81, s77
	ml_cvt_bf16_f32  v40, v40
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_store_b16  v75, v55, s80, #260, null
	.loc	1 579 31                        ; generated_attention.py:579:31
	ml_cvt_bf16_f32  v75, v86
	ml_byte_permute_b32 v45, v45, v75, s77
	ml_cvt_bf16_f32  v37, v37
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_store_b16  v85, v55, s81, #0, null
	.loc	1 579 31                        ; generated_attention.py:579:31
	ml_byte_permute_b32 v41, v41, v44, s77
	ml_byte_permute_b32 v39, v39, v42, s77
	ml_cvt_bf16_f32  v38, v38
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_store_b16  v76, v55, s81, #4, null
	.loc	1 579 31                        ; generated_attention.py:579:31
	ml_byte_permute_b32 v76, v79, v78, s77
	ml_byte_permute_b32 v78, v67, v67, s78
	ml_pk_shl_b16 v78, v78, 0x40004
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_store_b16  v84, v55, s81, #256, null
	.loc	1 579 31                        ; generated_attention.py:579:31
	ml_byte_permute_b32 v79, v68, v68, s78
	ml_pk_shl_b16 v79, v79, 0x40004
	ml_pk_srl_b8 v79, v79, 0x40004
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_store_b16  v74, v55, s81, #260, null
	.loc	1 579 31                        ; generated_attention.py:579:31
	ml_pk_srl_b8 v74, v78, 0x40004
	ml_byte_permute_b32 v78, v76, v47, v74
	ml_byte_permute_b32 v47, v76, v47, v79
	ml_slb_shuffle_rtn_b32 v78, v78, v71
	ml_byte_permute_b32 v46, v45, v43, v74
	ml_byte_permute_b32 v43, v45, v43, v79
	ml_byte_permute_b32 v42, v41, v39, v74
	ml_slb_shuffle_rtn_b32 v47, v47, v72
	ml_cvt_bf16_f32  v36, v36
	ml_byte_permute_b32 v39, v41, v39, v79
	ml_byte_permute_b32 v37, v37, v40, s77
	ml_slb_shuffle_rtn_b32 v46, v46, v71
	ml_byte_permute_b32 v36, v36, v38, s77
	ml_byte_permute_b32 v38, v37, v36, v74
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_srl_b32 v45, v80, 0x10
	.loc	1 579 31                        ; generated_attention.py:579:31
	ml_slb_shuffle_rtn_b32 v43, v43, v72
	ml_byte_permute_b32 v36, v37, v36, v79
	ml_byte_permute_b32 v37, v69, v69, s78
	ml_slb_shuffle_rtn_b32 v42, v42, v71
	ml_slb_shuffle_rtn_b32 v41, v39, v72
	ml_slb_shuffle_rtn_b32 v44, v38, v71
	ml_slb_shuffle_rtn_b32 v74, v36, v72
	ml_pk_shl_b16 v36, v37, 0x40004
	ml_pk_srl_b8 v75, v36, 0x40004
	sl_wait lmcnt(6)
	ml_byte_permute_b32 v36, v78, v47, v75
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_store_b16  v82, v55, s82, #0, null
	.loc	1 579 31                        ; generated_attention.py:579:31
	ml_byte_permute_b32 v37, v70, v70, s78
	ml_pk_shl_b16 v37, v37, 0x40004
	ml_pk_srl_b8 v76, v37, 0x40004
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_store_b16  v77, v55, s82, #4, null
	.loc	1 579 31                        ; generated_attention.py:579:31
	ml_byte_permute_b32 v37, v78, v47, v76
	sl_wait lmcnt(6)
	ml_byte_permute_b32 v38, v46, v43, v75
	ml_byte_permute_b32 v39, v46, v43, v76
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_store_b16  v80, v55, s82, #256, null
	.loc	1 579 31                        ; generated_attention.py:579:31
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v40, v42, v41, v75
	ml_byte_permute_b32 v41, v42, v41, v76
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_store_b16  v45, v55, s82, #260, null
	.loc	1 579 31                        ; generated_attention.py:579:31
	sl_wait lmcnt(4)
	ml_byte_permute_b32 v42, v44, v74, v75
	ml_byte_permute_b32 v43, v44, v74, v76
	.loc	1 553 16                        ; generated_attention.py:553:16
	sl_wait lmcnt(0)
	sl_barrier 
	ml_slb_blkload_x1  v44, noreg, s79, #0, null
	.loc	1 403 28                        ; generated_attention.py:403:28
	sl_add_i64 s[58:59], s[58:59], 0x1
	sl_xor_b64 {s[6:7], wcr}, s[58:59], s[42:43]
	ml_mov_b32 v77, v32
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v45, noreg, s79, #256, null
	ml_mov_b32 v76, v33
	ml_mov_b32 v75, v34
	ml_mov_b32 v74, v35
	ml_slb_load_b32x1  v46, v73, s79, #512, null
	ml_slb_load_b32x1  v47, v73, s79, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[36:37], v[44:45], v[24:27]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v44, noreg, s86, #0, null
	ml_slb_blkload_x1  v45, noreg, s86, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[36:37], v[46:47], v[28:31]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v46, v73, s86, #512, null
	ml_slb_load_b32x1  v47, v73, s86, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[36:37], v[44:45], v[16:19]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v44, noreg, s87, #0, null
	ml_slb_blkload_x1  v45, noreg, s87, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[36:37], v[46:47], v[20:23]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v46, v73, s87, #512, null
	ml_slb_load_b32x1  v47, v73, s87, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[36:37], v[44:45], v[8:11]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v44, noreg, s88, #0, null
	ml_slb_blkload_x1  v45, noreg, s88, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[36:37], v[46:47], v[12:15]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v46, v73, s88, #512, null
	ml_slb_load_b32x1  v47, v73, s88, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[36:37], v[44:45], v[4:7]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v44, noreg, s80, #0, null
	ml_slb_blkload_x1  v45, noreg, s80, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[36:37], v[46:47], v[0:3]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v36, v73, s80, #512, null
	ml_slb_load_b32x1  v37, v73, s80, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[38:39], v[44:45], v[24:27]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v44, noreg, s89, #0, null
	ml_slb_blkload_x1  v45, noreg, s89, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[38:39], v[36:37], v[28:31]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v36, v73, s89, #512, null
	ml_slb_load_b32x1  v37, v73, s89, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[38:39], v[44:45], v[16:19]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v44, noreg, s90, #0, null
	ml_slb_blkload_x1  v45, noreg, s90, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[38:39], v[36:37], v[20:23]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v36, v73, s90, #512, null
	ml_slb_load_b32x1  v37, v73, s90, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[38:39], v[44:45], v[8:11]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v44, noreg, s91, #0, null
	ml_slb_blkload_x1  v45, noreg, s91, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[38:39], v[36:37], v[12:15]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v36, v73, s91, #512, null
	ml_slb_load_b32x1  v37, v73, s91, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[38:39], v[44:45], v[4:7]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v44, noreg, s81, #0, null
	ml_slb_blkload_x1  v45, noreg, s81, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[38:39], v[36:37], v[0:3]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v36, v73, s81, #512, null
	ml_slb_load_b32x1  v37, v73, s81, #768, null
	ml_slb_blkload_x1  v38, noreg, s92, #0, null
	ml_slb_blkload_x1  v39, noreg, s92, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[40:41], v[44:45], v[24:27]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[40:41], v[36:37], v[28:31]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v36, v73, s92, #512, null
	ml_slb_load_b32x1  v37, v73, s92, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[40:41], v[38:39], v[16:19]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v38, noreg, s93, #0, null
	ml_slb_blkload_x1  v39, noreg, s93, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[40:41], v[36:37], v[20:23]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v36, v73, s93, #512, null
	ml_slb_load_b32x1  v37, v73, s93, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[40:41], v[38:39], v[8:11]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v38, noreg, s94, #0, null
	ml_slb_blkload_x1  v39, noreg, s94, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[40:41], v[36:37], v[12:15]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v36, v73, s94, #512, null
	ml_slb_load_b32x1  v37, v73, s94, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[40:41], v[38:39], v[4:7]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v38, noreg, s82, #0, null
	ml_slb_blkload_x1  v39, noreg, s82, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[40:41], v[36:37], v[0:3]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v36, v73, s82, #512, null
	ml_slb_load_b32x1  v37, v73, s82, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[42:43], v[38:39], v[24:27]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v38, noreg, s37, #0, null
	ml_slb_blkload_x1  v39, noreg, s37, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[42:43], v[36:37], v[28:31]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v36, v73, s37, #512, null
	ml_slb_load_b32x1  v37, v73, s37, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[42:43], v[38:39], v[16:19]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v38, noreg, s4, #0, null
	ml_slb_blkload_x1  v39, noreg, s4, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[42:43], v[36:37], v[20:23]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v36, v73, s4, #512, null
	ml_slb_load_b32x1  v37, v73, s4, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[42:43], v[38:39], v[8:11]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_blkload_x1  v38, noreg, s5, #0, null
	ml_slb_blkload_x1  v39, noreg, s5, #256, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[42:43], v[36:37], v[12:15]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_slb_load_b32x1  v36, v73, s5, #512, null
	ml_slb_load_b32x1  v37, v73, s5, #768, null
	.loc	1 579 41                        ; generated_attention.py:579:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[42:43], v[38:39], v[4:7]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[42:43], v[36:37], v[0:3]
	.loc	1 403 28                        ; generated_attention.py:403:28
	sl_cbr_wcrz BB0_71, wcr
BB0_38:                                 ; =>This Inner Loop Header: Depth=1
	.loc	1 404 25                        ; generated_attention.py:404:25
	sl_shl_b64 {s[60:61], wcr}, s[58:59], 0x6
	.loc	1 404 37 is_stmt 0              ; generated_attention.py:404:37
	sl_or_b64 {s[64:65], wcr}, s[60:61], s[84:85]
	.loc	1 405 33 is_stmt 1              ; generated_attention.py:405:33
	sl_min_i64 s[6:7], s[64:65], s[26:27]
	sl_xor_b64 {s[6:7], wcr}, s[6:7], s[26:27]
	sl_sub_bi_u64 tcr, s[10:11], s[10:11], wcr
	sl_sub_bi_u32 s6, s10, s10, wcr
	.loc	1 408 52                        ; generated_attention.py:408:52
	sl_srl_b64 {s[8:9], wcr}, s[60:61], 0x2
	sl_add_i64 s[20:21], s[32:33], s[8:9]
	.loc	1 408 12 is_stmt 0              ; generated_attention.py:408:12
	ml_lsa_load_dword v32, s[20:23], noreg, noreg, #0, ca
	.loc	1 466 32 is_stmt 1              ; generated_attention.py:466:32
	sl_shl_b64 {s[66:67], wcr}, s[46:47], 0x1
	.loc	1 408 12                        ; generated_attention.py:408:12
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s70, v32, 0x0
	ml_mov_b32 v32, 0x0
	sl_sra_b32 {s71, wcr}, s70, 0x1f
	.loc	1 459 46                        ; generated_attention.py:459:46
	sl_mul_u64_u32 s[8:9], s56, s70
	sl_mull_u32 s7, s57, s70
	sl_mull_u32 s12, s56, s71
	sl_add_i32 s9, s9, s12
	sl_add_i32 s9, s9, s7
	.loc	1 466 32                        ; generated_attention.py:466:32
	sl_shl_b64 {s[8:9], wcr}, s[8:9], 0x1
	sl_add_i64 s[12:13], s[34:35], s[8:9]
	.loc	1 466 16 is_stmt 0              ; generated_attention.py:466:16
	sl_or_b32 {s6, wcr}, s6, 0x0
	sl_cbr_wcrz BB0_40, wcr
; %bb.39:                               ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 0 16                          ; generated_attention.py:0:16
	sl_add_i64 s[28:29], s[12:13], s[66:67]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_lsa_blkload_x1 v32, s[28:31], noreg, noreg, #0, ca
BB0_40:                                 ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 404 37 is_stmt 1              ; generated_attention.py:404:37
	sl_or_b32 {s6, wcr}, s64, 0x8
	sl_mov_b32 s7, s65
	.loc	1 405 33                        ; generated_attention.py:405:33
	sl_min_i64 s[6:7], s[6:7], s[26:27]
	sl_xor_b64 {s[6:7], wcr}, s[6:7], s[26:27]
	sl_sub_bi_u64 s[8:9], s[10:11], s[10:11], wcr
	ml_mov_b32 v33, 0x0
	.loc	1 466 16                        ; generated_attention.py:466:16
	sl_cbr_wcrz BB0_42, wcr
; %bb.41:                               ;   in Loop: Header=BB0_38 Depth=1
	sl_shl_b64 {s[6:7], wcr}, s[44:45], 0x1
	sl_add_i64 s[28:29], s[12:13], s[6:7]
	ml_lsa_blkload_x1 v33, s[28:31], noreg, noreg, #0, ca
BB0_42:                                 ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s6, s64, 0x10
	sl_mov_b32 s7, s65
	sl_srl_b64 {s[12:13], wcr}, s[6:7], 0x2
	sl_and_b32 {s12, wcr}, s12, 0xfffffff4
	sl_add_i64 s[20:21], s[32:33], s[12:13]
	ml_lsa_load_dword v34, s[20:23], noreg, noreg, #0, ca
	ml_mov_b32 v35, 0x0
	.loc	1 405 33 is_stmt 1              ; generated_attention.py:405:33
	sl_min_i64 s[12:13], s[6:7], s[26:27]
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s22, v34, 0x0
	.loc	1 466 16 is_stmt 1              ; generated_attention.py:466:16
	ml_mov_b32 v34, 0x0
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_sra_b32 {s76, wcr}, s22, 0x1f
	sl_mul_u64_u32 s[6:7], s56, s22
	sl_mull_u32 s14, s57, s22
	sl_mull_u32 s15, s56, s76
	.loc	1 405 33 is_stmt 1              ; generated_attention.py:405:33
	sl_xor_b64 {s[12:13], wcr}, s[12:13], s[26:27]
	sl_sub_bi_u64 s[12:13], s[10:11], s[10:11], wcr
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s7, s7, s15
	sl_add_i32 s7, s7, s14
	.loc	1 466 16 is_stmt 1              ; generated_attention.py:466:16
	sl_cbr_wcrz BB0_44, wcr
; %bb.43:                               ;   in Loop: Header=BB0_38 Depth=1
	sl_add_i64 s[14:15], s[34:35], s[66:67]
	sl_shl_b64 {s[16:17], wcr}, s[6:7], 0x1
	sl_add_i64 s[28:29], s[14:15], s[16:17]
	ml_lsa_blkload_x1 v35, s[28:31], noreg, noreg, #0, ca
BB0_44:                                 ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 404 37                        ; generated_attention.py:404:37
	sl_or_b32 {s14, wcr}, s64, 0x18
	sl_mov_b32 s15, s65
	.loc	1 405 33                        ; generated_attention.py:405:33
	sl_min_i64 s[14:15], s[14:15], s[26:27]
	sl_xor_b64 {s[14:15], wcr}, s[14:15], s[26:27]
	sl_sub_bi_u64 s[14:15], s[10:11], s[10:11], wcr
	.loc	1 466 16                        ; generated_attention.py:466:16
	sl_cbr_wcrz BB0_46, wcr
; %bb.45:                               ;   in Loop: Header=BB0_38 Depth=1
	sl_shl_b64 {s[16:17], wcr}, s[44:45], 0x1
	sl_add_i64 s[16:17], s[34:35], s[16:17]
	sl_shl_b64 {s[6:7], wcr}, s[6:7], 0x1
	sl_add_i64 s[28:29], s[16:17], s[6:7]
	ml_lsa_blkload_x1 v34, s[28:31], noreg, noreg, #0, ca
BB0_46:                                 ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s6, s64, 0x20
	sl_mov_b32 s7, s65
	sl_srl_b64 {s[16:17], wcr}, s[6:7], 0x2
	sl_and_b32 {s16, wcr}, s16, 0xfffffff8
	sl_add_i64 s[20:21], s[32:33], s[16:17]
	ml_lsa_load_dword v36, s[20:23], noreg, noreg, #0, ca
	ml_mov_b32 v37, 0x0
	.loc	1 405 33 is_stmt 1              ; generated_attention.py:405:33
	sl_min_i64 s[16:17], s[6:7], s[26:27]
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s38, v36, 0x0
	.loc	1 466 16 is_stmt 1              ; generated_attention.py:466:16
	ml_mov_b32 v36, 0x0
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_sra_b32 {s39, wcr}, s38, 0x1f
	sl_mul_u64_u32 s[6:7], s56, s38
	sl_mull_u32 s18, s57, s38
	sl_mull_u32 s19, s56, s39
	.loc	1 405 33 is_stmt 1              ; generated_attention.py:405:33
	sl_xor_b64 {s[16:17], wcr}, s[16:17], s[26:27]
	sl_sub_bi_u64 s[16:17], s[10:11], s[10:11], wcr
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s7, s7, s19
	sl_add_i32 s7, s7, s18
	.loc	1 466 16 is_stmt 1              ; generated_attention.py:466:16
	sl_cbr_wcrz BB0_48, wcr
; %bb.47:                               ;   in Loop: Header=BB0_38 Depth=1
	sl_add_i64 s[18:19], s[34:35], s[66:67]
	sl_shl_b64 {s[20:21], wcr}, s[6:7], 0x1
	sl_add_i64 s[28:29], s[18:19], s[20:21]
	ml_lsa_blkload_x1 v37, s[28:31], noreg, noreg, #0, ca
BB0_48:                                 ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 404 37                        ; generated_attention.py:404:37
	sl_or_b32 {s18, wcr}, s64, 0x28
	sl_mov_b32 s19, s65
	.loc	1 405 33                        ; generated_attention.py:405:33
	sl_min_i64 s[18:19], s[18:19], s[26:27]
	sl_xor_b64 {s[18:19], wcr}, s[18:19], s[26:27]
	sl_sub_bi_u64 s[18:19], s[10:11], s[10:11], wcr
	.loc	1 466 16                        ; generated_attention.py:466:16
	sl_cbr_wcrz BB0_50, wcr
; %bb.49:                               ;   in Loop: Header=BB0_38 Depth=1
	sl_shl_b64 {s[20:21], wcr}, s[44:45], 0x1
	sl_add_i64 s[20:21], s[34:35], s[20:21]
	sl_shl_b64 {s[6:7], wcr}, s[6:7], 0x1
	sl_add_i64 s[28:29], s[20:21], s[6:7]
	ml_lsa_blkload_x1 v36, s[28:31], noreg, noreg, #0, ca
BB0_50:                                 ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s6, s64, 0x30
	sl_mov_b32 s7, s65
	sl_srl_b64 {s[20:21], wcr}, s[6:7], 0x2
	sl_and_b32 {s20, wcr}, s20, 0xfffffffc
	sl_add_i64 s[20:21], s[32:33], s[20:21]
	ml_lsa_load_dword v38, s[20:23], noreg, noreg, #0, ca
	ml_mov_b32 v39, 0x0
	.loc	1 405 33 is_stmt 1              ; generated_attention.py:405:33
	sl_min_i64 s[6:7], s[6:7], s[26:27]
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s50, v38, 0x0
	.loc	1 466 16 is_stmt 1              ; generated_attention.py:466:16
	ml_mov_b32 v38, 0x0
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_sra_b32 {s51, wcr}, s50, 0x1f
	sl_mul_u64_u32 s[68:69], s56, s50
	sl_mull_u32 s28, s57, s50
	sl_mull_u32 s29, s56, s51
	.loc	1 405 33 is_stmt 1              ; generated_attention.py:405:33
	sl_xor_b64 {s[6:7], wcr}, s[6:7], s[26:27]
	sl_sub_bi_u64 s[20:21], s[10:11], s[10:11], wcr
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_add_i32 s6, s69, s29
	sl_add_i32 s69, s6, s28
	.loc	1 466 16 is_stmt 1              ; generated_attention.py:466:16
	sl_cbr_wcrz BB0_52, wcr
; %bb.51:                               ;   in Loop: Header=BB0_38 Depth=1
	sl_add_i64 s[6:7], s[34:35], s[66:67]
	sl_shl_b64 {s[28:29], wcr}, s[68:69], 0x1
	sl_add_i64 s[28:29], s[6:7], s[28:29]
	ml_lsa_blkload_x1 v39, s[28:31], noreg, noreg, #0, ca
BB0_52:                                 ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 404 37                        ; generated_attention.py:404:37
	sl_or_b32 {s64, wcr}, s64, 0x38
	.loc	1 405 33                        ; generated_attention.py:405:33
	sl_min_i64 s[6:7], s[64:65], s[26:27]
	sl_xor_b64 {s[6:7], wcr}, s[6:7], s[26:27]
	sl_sub_bi_u64 s[6:7], s[10:11], s[10:11], wcr
	.loc	1 466 16                        ; generated_attention.py:466:16
	sl_cbr_wcrz BB0_54, wcr
; %bb.53:                               ;   in Loop: Header=BB0_38 Depth=1
	sl_shl_b64 {s[28:29], wcr}, s[44:45], 0x1
	sl_add_i64 s[28:29], s[34:35], s[28:29]
	sl_shl_b64 {s[52:53], wcr}, s[68:69], 0x1
	sl_add_i64 s[28:29], s[28:29], s[52:53]
	ml_lsa_blkload_x1 v38, s[28:31], noreg, noreg, #0, ca
BB0_54:                                 ;   in Loop: Header=BB0_38 Depth=1
	sl_wait vmcnt(0) lmcnt(0)
	sl_barrier 
	ml_slb_store_b32x1  v32, v60, s79, #0, null
	ml_slb_store_b32x1  v35, v60, s80, #0, null
	ml_slb_store_b32x1  v37, v60, s81, #0, null
	ml_slb_store_b32x1  v39, v60, s82, #0, null
	ml_slb_store_b32x1  v33, v61, s79, #512, null
	ml_slb_store_b32x1  v34, v61, s80, #512, null
	ml_slb_store_b32x1  v36, v61, s81, #512, null
	ml_slb_store_b32x1  v38, v61, s82, #512, null
	.loc	1 353 12                        ; generated_attention.py:353:12
	sl_wait lmcnt(0)
	sl_barrier 
	ml_slb_blkload_x1  v78, noreg, s73, #0, null
	sl_add_i32 s28, s73, 0x400
	sl_add_i32 s29, s73, 0x800
	sl_add_i32 s52, s73, 0xc00
	ml_slb_blkload_x1  v79, noreg, s73, #256, null
	sl_mov_b32 s53, 0x400
	.loc	1 524 41                        ; generated_attention.py:524:41
	ml_mov_b32 v32, 0x0
	ml_mov_b32 v33, v49
	.loc	1 353 12                        ; generated_attention.py:353:12
	ml_slb_blkload_x1  v80, noreg, s28, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	ml_mov_b32 v34, v49
	ml_mov_b32 v35, v49
	.loc	1 547 46                        ; generated_attention.py:547:46
	sl_mul_u64_u32 s[64:65], s62, s70
	.loc	1 353 12                        ; generated_attention.py:353:12
	ml_slb_blkload_x1  v81, noreg, s28, #256, null
	ml_slb_blkload_x1  v82, noreg, s29, #0, null
	ml_slb_blkload_x1  v83, noreg, s29, #256, null
	ml_slb_blkload_x1  v84, noreg, s52, #0, null
	ml_slb_blkload_x1  v85, noreg, s52, #256, null
	ml_slb_load_b32x1  v86, v62, noreg, #512, null
	ml_slb_load_b32x1  v87, v62, noreg, #768, null
	ml_slb_load_b32x1  v88, v62, s53, #512, null
	ml_slb_load_b32x1  v89, v62, s53, #768, null
	sl_mov_b32 s53, 0xc00
	ml_slb_load_b32x1  v90, v62, s83, #512, null
	ml_slb_load_b32x1  v91, v62, s83, #768, null
	ml_slb_load_b32x1  v92, v62, s53, #512, null
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v36, v63, s79, #0, null
	ml_slb_load_b32x1  v37, v64, s79, #0, null
	ml_slb_load_b32x1  v38, v63, s80, #0, null
	ml_slb_load_b32x1  v39, v64, s80, #0, null
	ml_slb_load_b32x1  v93, v63, s81, #0, null
	ml_slb_load_b32x1  v94, v64, s81, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[78:79], v[36:37], v[32:35]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v95, v63, s82, #0, null
	ml_slb_load_b32x1  v96, v64, s82, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[78:79], v[38:39], v[32:35]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v97, v65, s79, #0, null
	ml_slb_load_b32x1  v98, v66, s79, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[78:79], v[93:94], v[32:35]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v93, v65, s80, #0, null
	ml_slb_load_b32x1  v94, v66, s80, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[78:79], v[95:96], v[32:35]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v78, v65, s81, #0, null
	ml_slb_load_b32x1  v79, v66, s81, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[86:87], v[97:98], v[44:47]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v95, v65, s82, #0, null
	ml_slb_load_b32x1  v96, v66, s82, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[86:87], v[93:94], v[40:43]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v93, v63, s86, #0, null
	ml_slb_load_b32x1  v94, v64, s86, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[86:87], v[78:79], v[36:39]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v78, v63, s89, #0, null
	ml_slb_load_b32x1  v79, v64, s89, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[86:87], v[95:96], v[32:35]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v86, v63, s92, #0, null
	ml_slb_load_b32x1  v87, v64, s92, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[80:81], v[93:94], v[44:47]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v93, v63, s37, #0, null
	ml_slb_load_b32x1  v94, v64, s37, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[80:81], v[78:79], v[40:43]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v78, v65, s86, #0, null
	ml_slb_load_b32x1  v79, v66, s86, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[80:81], v[86:87], v[36:39]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v86, v65, s89, #0, null
	ml_slb_load_b32x1  v87, v66, s89, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[80:81], v[93:94], v[32:35]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v80, v65, s92, #0, null
	ml_slb_load_b32x1  v81, v66, s92, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[88:89], v[78:79], v[44:47]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v78, v65, s37, #0, null
	ml_slb_load_b32x1  v79, v66, s37, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[88:89], v[86:87], v[40:43]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v86, v63, s87, #0, null
	ml_slb_load_b32x1  v87, v64, s87, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[88:89], v[80:81], v[36:39]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v80, v63, s90, #0, null
	ml_slb_load_b32x1  v81, v64, s90, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[88:89], v[78:79], v[32:35]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v78, v63, s93, #0, null
	ml_slb_load_b32x1  v79, v64, s93, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[82:83], v[86:87], v[44:47]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v86, v63, s4, #0, null
	ml_slb_load_b32x1  v87, v64, s4, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[82:83], v[80:81], v[40:43]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v80, v65, s87, #0, null
	ml_slb_load_b32x1  v81, v66, s87, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[82:83], v[78:79], v[36:39]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v78, v65, s90, #0, null
	ml_slb_load_b32x1  v79, v66, s90, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[82:83], v[86:87], v[32:35]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v82, v65, s93, #0, null
	ml_slb_load_b32x1  v83, v66, s93, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[90:91], v[80:81], v[44:47]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v80, v65, s4, #0, null
	ml_slb_load_b32x1  v81, v66, s4, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[90:91], v[78:79], v[40:43]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v78, v63, s88, #0, null
	ml_slb_load_b32x1  v79, v64, s88, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[90:91], v[82:83], v[36:39]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v82, v63, s91, #0, null
	ml_slb_load_b32x1  v83, v64, s91, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[90:91], v[80:81], v[32:35]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v80, v63, s94, #0, null
	ml_slb_load_b32x1  v81, v64, s94, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[84:85], v[78:79], v[44:47]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v78, v63, s5, #0, null
	ml_slb_load_b32x1  v79, v64, s5, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[84:85], v[82:83], v[40:43]
	.loc	1 353 12                        ; generated_attention.py:353:12
	ml_slb_load_b32x1  v93, v62, s53, #768, null
	.loc	1 547 46                        ; generated_attention.py:547:46
	sl_mull_u32 s53, s62, s71
	sl_add_i32 s53, s65, s53
	sl_mull_u32 s65, s63, s70
	sl_add_i32 s65, s53, s65
	.loc	1 553 34                        ; generated_attention.py:553:34
	sl_shl_b64 {s[64:65], wcr}, s[64:65], 0x1
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[84:85], v[80:81], v[36:39]
	.loc	1 553 34                        ; generated_attention.py:553:34
	sl_add_i64 s[66:67], s[40:41], s[64:65]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v80, v65, s88, #0, null
	.loc	1 553 34                        ; generated_attention.py:553:34
	sl_shl_b64 {s[64:65], wcr}, s[54:55], 0x1
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v81, v66, s88, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[84:85], v[78:79], v[32:35]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v78, v65, s91, #0, null
	ml_slb_load_b32x1  v79, v66, s91, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[44:47], v[92:93], v[80:81], v[44:47]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v80, v65, s94, #0, null
	ml_slb_load_b32x1  v81, v66, s94, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[40:43], v[92:93], v[78:79], v[40:43]
	.loc	1 466 16                        ; generated_attention.py:466:16
	ml_slb_load_b32x1  v78, v65, s5, #0, null
	ml_slb_load_b32x1  v79, v66, s5, #0, null
	.loc	1 524 41                        ; generated_attention.py:524:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[36:39], v[92:93], v[80:81], v[36:39]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[32:35], v[92:93], v[78:79], v[32:35]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_mov_b32 v78, 0x0
	ml_mov_b32 v79, 0x0
	sl_cbr_tcraz BB0_56, tcr
; %bb.55:                               ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 0 16 is_stmt 0                ; generated_attention.py:0:16
	sl_add_i64 s[28:29], s[66:67], s[64:65]
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_lsa_blkload_x1 v79, s[28:31], noreg, noreg, #0, ca
BB0_56:                                 ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 0 0                           ; generated_attention.py:0
	sl_mov_b64 tcr, s[8:9]
	.loc	1 553 16                        ; generated_attention.py:553:16
	sl_cbr_tcraz BB0_58, tcr
; %bb.57:                               ;   in Loop: Header=BB0_38 Depth=1
	sl_shl_b64 {s[8:9], wcr}, s[48:49], 0x1
	sl_add_i64 s[28:29], s[66:67], s[8:9]
	ml_lsa_blkload_x1 v78, s[28:31], noreg, noreg, #0, ca
BB0_58:                                 ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 0 0                           ; generated_attention.py:0
	sl_mull_u32 s28, s62, s76
	sl_mul_u64_u32 s[8:9], s62, s22
	sl_add_i32 s9, s9, s28
	sl_mull_u32 s22, s63, s22
	sl_add_i32 s9, s9, s22
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_mov_b32 v81, 0x0
	.loc	1 0 0                           ; generated_attention.py:0
	sl_mov_b64 tcr, s[12:13]
	ml_mov_b32 v83, 0x0
	.loc	1 553 16                        ; generated_attention.py:553:16
	sl_cbr_tcraz BB0_60, tcr
; %bb.59:                               ;   in Loop: Header=BB0_38 Depth=1
	sl_add_i64 s[12:13], s[40:41], s[64:65]
	sl_shl_b64 {s[28:29], wcr}, s[8:9], 0x1
	sl_add_i64 s[28:29], s[12:13], s[28:29]
	ml_lsa_blkload_x1 v83, s[28:31], noreg, noreg, #0, ca
BB0_60:                                 ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 0 0                           ; generated_attention.py:0
	sl_mov_b64 tcr, s[14:15]
	.loc	1 553 16                        ; generated_attention.py:553:16
	sl_cbr_tcraz BB0_62, tcr
; %bb.61:                               ;   in Loop: Header=BB0_38 Depth=1
	sl_shl_b64 {s[12:13], wcr}, s[48:49], 0x1
	sl_add_i64 s[12:13], s[40:41], s[12:13]
	sl_shl_b64 {s[8:9], wcr}, s[8:9], 0x1
	sl_add_i64 s[28:29], s[12:13], s[8:9]
	ml_lsa_blkload_x1 v81, s[28:31], noreg, noreg, #0, ca
BB0_62:                                 ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 0 0                           ; generated_attention.py:0
	sl_mull_u32 s12, s62, s39
	sl_mul_u64_u32 s[8:9], s62, s38
	sl_add_i32 s9, s9, s12
	sl_mull_u32 s12, s63, s38
	sl_add_i32 s9, s9, s12
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_mov_b32 v84, 0x0
	.loc	1 0 0                           ; generated_attention.py:0
	sl_mov_b64 tcr, s[16:17]
	ml_mov_b32 v85, 0x0
	.loc	1 553 16                        ; generated_attention.py:553:16
	sl_cbr_tcraz BB0_64, tcr
; %bb.63:                               ;   in Loop: Header=BB0_38 Depth=1
	sl_add_i64 s[12:13], s[40:41], s[64:65]
	sl_shl_b64 {s[14:15], wcr}, s[8:9], 0x1
	sl_add_i64 s[28:29], s[12:13], s[14:15]
	ml_lsa_blkload_x1 v85, s[28:31], noreg, noreg, #0, ca
BB0_64:                                 ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 0 0                           ; generated_attention.py:0
	sl_mov_b64 tcr, s[18:19]
	.loc	1 553 16                        ; generated_attention.py:553:16
	sl_cbr_tcraz BB0_66, tcr
; %bb.65:                               ;   in Loop: Header=BB0_38 Depth=1
	sl_shl_b64 {s[12:13], wcr}, s[48:49], 0x1
	sl_add_i64 s[12:13], s[40:41], s[12:13]
	sl_shl_b64 {s[8:9], wcr}, s[8:9], 0x1
	sl_add_i64 s[28:29], s[12:13], s[8:9]
	ml_lsa_blkload_x1 v84, s[28:31], noreg, noreg, #0, ca
BB0_66:                                 ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 0 0                           ; generated_attention.py:0
	sl_mull_u32 s8, s62, s51
	sl_mul_u64_u32 s[18:19], s62, s50
	sl_add_i32 s8, s19, s8
	sl_mull_u32 s9, s63, s50
	sl_add_i32 s19, s8, s9
	.loc	1 553 16                        ; generated_attention.py:553:16
	ml_mov_b32 v80, 0x0
	.loc	1 0 0                           ; generated_attention.py:0
	sl_mov_b64 tcr, s[20:21]
	ml_mov_b32 v82, 0x0
	.loc	1 553 16                        ; generated_attention.py:553:16
	sl_cbr_tcraz BB0_68, tcr
; %bb.67:                               ;   in Loop: Header=BB0_38 Depth=1
	sl_add_i64 s[8:9], s[40:41], s[64:65]
	sl_shl_b64 {s[12:13], wcr}, s[18:19], 0x1
	sl_add_i64 s[28:29], s[8:9], s[12:13]
	ml_lsa_blkload_x1 v82, s[28:31], noreg, noreg, #0, ca
BB0_68:                                 ;   in Loop: Header=BB0_38 Depth=1
	.loc	1 0 0                           ; generated_attention.py:0
	ml_or_b32 v86, s60, v58
	ml_add_i32 v87, v86, 0x10
	ml_add_i32 v88, v86, 0x20
	ml_add_i32 v89, v86, 0x30
	sl_cmp_eq_u32 wcr, s61, s75
	sl_sub_bi_u64 s[8:9], s[10:11], s[10:11], wcr
	ml_cmp_ge_u32 tcr, s72, v86
	ml_fma_f32 v44, s36, v44, 0
	ml_fma_f32 v45, s36, v45, 0
	ml_fma_f32 v46, s36, v46, 0
	sl_and_b64 {s[8:9], wcr}, s[8:9], tcr
	sl_cmp_lt_i32 wcr, s61, s75
	sl_sub_bi_u64 s[12:13], s[10:11], s[10:11], wcr
	sl_or_b64 {s[20:21], wcr}, s[8:9], s[12:13]
	sl_cmp_eq_u32 wcr, s61, s74
	sl_sub_bi_u64 s[8:9], s[10:11], s[10:11], wcr
	ml_cmp_ge_u32 tcr, s30, v86
	ml_mov_b32 v86, s75
	ml_fma_f32 v47, s36, v47, 0
	ml_fma_f32 v40, s36, v40, 0
	sl_and_b64 {s[8:9], wcr}, s[8:9], tcr
	sl_cmp_lt_i32 wcr, s61, s74
	sl_sub_bi_u64 s[12:13], s[10:11], s[10:11], wcr
	sl_or_b64 {s[28:29], wcr}, s[8:9], s[12:13]
	ml_cmp_ge_u32 tcr, s72, v87
	ml_fma_f32 v41, s36, v41, 0
	ml_fma_f32 v42, s36, v42, 0
	ml_fma_f32 v43, s36, v43, 0
	sl_mov_b64 s[8:9], tcr
	ml_cmp_eq_u32 tcr, s61, v86
	ml_fma_f32 v36, s36, v36, 0
	ml_fma_f32 v37, s36, v37, 0
	ml_fma_f32 v38, s36, v38, 0
	sl_mov_b64 s[12:13], tcr
	sl_and_b64 {s[14:15], wcr}, tcr, s[8:9]
	ml_cmp_lt_i32 tcr, s61, v86
	ml_mov_b32 v86, s74
	ml_fma_f32 v39, s36, v39, 0
	ml_fma_f32 v32, s36, v32, 0
	sl_mov_b64 s[8:9], tcr
	sl_or_b64 {s[38:39], wcr}, s[14:15], tcr
	ml_cmp_ge_u32 tcr, s30, v87
	ml_fma_f32 v33, s36, v33, 0
	ml_mov_b32 v90, 0xff800000
	sl_mov_b64 s[14:15], tcr
	ml_cmp_eq_u32 tcr, s61, v86
	sl_mov_b64 s[16:17], tcr
	sl_and_b64 {s[50:51], wcr}, tcr, s[14:15]
	ml_cmp_lt_i32 tcr, s61, v86
	sl_mov_b64 s[14:15], tcr
	sl_or_b64 {s[50:51], wcr}, s[50:51], tcr
	ml_cmp_ge_u32 tcr, s72, v88
	sl_and_b64 {s[52:53], wcr}, s[12:13], tcr
	sl_or_b64 {s[52:53], wcr}, s[52:53], s[8:9]
	ml_cmp_ge_u32 tcr, s30, v88
	ml_fma_f32 v88, s36, v34, 0
	sl_and_b64 {s[60:61], wcr}, s[16:17], tcr
	sl_or_b64 {s[60:61], wcr}, s[60:61], s[14:15]
	ml_cmp_ge_u32 tcr, s72, v89
	sl_and_b64 {s[12:13], wcr}, s[12:13], tcr
	sl_or_b64 {s[8:9], wcr}, s[12:13], s[8:9]
	ml_cmp_ge_u32 tcr, s30, v89
	ml_fma_f32 v89, s36, v35, 0
	sl_and_b64 {s[12:13], wcr}, s[16:17], tcr
	sl_or_b64 {s[12:13], wcr}, s[12:13], s[14:15]
	sl_and_b64 {tcr, wcr}, s[2:3], s[20:21]
	ml_csel_b32 v34, v44, v90, tcr
	ml_csel_b32 v87, v45, v90, tcr
	sl_and_b64 {tcr, wcr}, s[0:1], s[28:29]
	ml_csel_b32 v35, v46, v90, tcr
	ml_csel_b32 v47, v47, v90, tcr
	sl_and_b64 {tcr, wcr}, s[2:3], s[38:39]
	ml_csel_b32 v86, v40, v90, tcr
	ml_csel_b32 v45, v41, v90, tcr
	sl_and_b64 {tcr, wcr}, s[0:1], s[50:51]
	ml_csel_b32 v46, v42, v90, tcr
	ml_csel_b32 v43, v43, v90, tcr
	sl_and_b64 {tcr, wcr}, s[2:3], s[52:53]
	ml_csel_b32 v44, v36, v90, tcr
	ml_csel_b32 v41, v37, v90, tcr
	sl_and_b64 {tcr, wcr}, s[0:1], s[60:61]
	ml_csel_b32 v42, v38, v90, tcr
	ml_csel_b32 v39, v39, v90, tcr
	sl_and_b64 {tcr, wcr}, s[2:3], s[8:9]
	ml_csel_b32 v40, v32, v90, tcr
	ml_csel_b32 v37, v33, v90, tcr
	sl_and_b64 {tcr, wcr}, s[0:1], s[12:13]
	ml_csel_b32 v38, v88, v90, tcr
	ml_csel_b32 v36, v89, v90, tcr
	ml_max_f32 v32, v34, v86
	ml_max_f32 v32, v32, v44
	ml_max_f32 v32, v32, v40
	ml_slb_shuffle_rtn_b32 v33, v32, v53
	ml_max_f32 v88, v87, v45
	ml_max_f32 v88, v88, v41
	ml_max_f32 v88, v88, v37
	ml_slb_shuffle_rtn_b32 v89, v88, v53
	ml_max_f32 v90, v35, v46
	ml_max_f32 v90, v90, v42
	ml_max_f32 v90, v90, v38
	ml_slb_shuffle_rtn_b32 v91, v90, v53
	ml_max_f32 v92, v47, v43
	ml_max_f32 v92, v92, v39
	ml_max_f32 v92, v92, v36
	ml_slb_shuffle_rtn_b32 v93, v92, v53
	.loc	1 553 16                        ; generated_attention.py:553:16
	sl_mov_b64 tcr, s[6:7]
	.loc	1 0 0                           ; generated_attention.py:0
	sl_wait lmcnt(3)
	ml_max_f32 v32, v32, v33
	ml_slb_shuffle_rtn_b32 v33, v32, v52
	sl_wait lmcnt(3)
	ml_max_f32 v88, v88, v89
	ml_slb_shuffle_rtn_b32 v89, v88, v52
	sl_wait lmcnt(3)
	ml_max_f32 v90, v90, v91
	ml_slb_shuffle_rtn_b32 v91, v90, v52
	sl_wait lmcnt(3)
	ml_max_f32 v92, v92, v93
	ml_slb_shuffle_rtn_b32 v93, v92, v52
	sl_wait lmcnt(3)
	ml_max_f32 v32, v32, v33
	ml_slb_shuffle_rtn_b32 v33, v32, v51
	sl_wait lmcnt(3)
	ml_max_f32 v88, v88, v89
	ml_slb_shuffle_rtn_b32 v89, v88, v51
	sl_wait lmcnt(3)
	ml_max_f32 v90, v90, v91
	ml_slb_shuffle_rtn_b32 v91, v90, v51
	sl_wait lmcnt(3)
	ml_max_f32 v92, v92, v93
	ml_slb_shuffle_rtn_b32 v93, v92, v51
	sl_wait lmcnt(3)
	ml_max_f32 v32, v32, v33
	ml_slb_shuffle_rtn_b32 v33, v32, v50
.Ltmp28:
	.loc	3 192 27 is_stmt 1              ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v32, v32, v33
.Ltmp29:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	ml_max_f32 v33, v88, v89
	ml_slb_shuffle_rtn_b32 v88, v33, v50
.Ltmp30:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v33, v33, v88
.Ltmp31:
	.loc	1 0 0                           ; generated_attention.py:0
	ml_max_f32 v88, v90, v91
	ml_slb_shuffle_rtn_b32 v89, v88, v50
.Ltmp32:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v88, v88, v89
.Ltmp33:
	.loc	1 0 0                           ; generated_attention.py:0
	ml_max_f32 v89, v92, v93
	ml_slb_shuffle_rtn_b32 v90, v89, v50
.Ltmp34:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v89, v89, v90
.Ltmp35:
	.loc	1 553 16 is_stmt 1              ; generated_attention.py:553:16
	sl_cbr_tcraz BB0_37, tcr
; %bb.69:                               ;   in Loop: Header=BB0_38 Depth=1
	sl_shl_b64 {s[6:7], wcr}, s[48:49], 0x1
	sl_add_i64 s[6:7], s[40:41], s[6:7]
	sl_shl_b64 {s[8:9], wcr}, s[18:19], 0x1
	sl_add_i64 s[28:29], s[6:7], s[8:9]
	ml_lsa_blkload_x1 v80, s[28:31], noreg, noreg, #0, ca
	sl_jump BB0_37
BB0_70:                                 ; %.thread34.._crit_edge63_crit_edge
.Ltmp36:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_xor_b32 v53, tid, 0x8
	ml_xor_b32 v52, tid, 0x4
	ml_xor_b32 v51, tid, 0x2
	ml_xor_b32 v50, tid, 0x1
	ml_mov_b32 v24, 0x0
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v25, 0x0
	ml_mov_b32 v26, 0x0
	ml_mov_b32 v27, 0x0
	ml_mov_b32 v28, 0x0
	ml_mov_b32 v29, 0x0
	ml_mov_b32 v30, 0x0
	ml_mov_b32 v31, 0x0
	ml_mov_b32 v16, 0x0
	ml_mov_b32 v17, 0x0
	ml_mov_b32 v18, 0x0
	ml_mov_b32 v19, 0x0
	ml_mov_b32 v20, 0x0
	ml_mov_b32 v21, 0x0
	ml_mov_b32 v22, 0x0
	ml_mov_b32 v23, 0x0
	ml_mov_b32 v8, 0x0
	ml_mov_b32 v9, 0x0
	ml_mov_b32 v10, 0x0
	ml_mov_b32 v11, 0x0
	ml_mov_b32 v12, 0x0
	ml_mov_b32 v13, 0x0
	ml_mov_b32 v14, 0x0
	ml_mov_b32 v15, 0x0
	ml_mov_b32 v4, 0x0
	ml_mov_b32 v5, 0x0
	ml_mov_b32 v6, 0x0
	ml_mov_b32 v7, 0x0
	ml_mov_b32 v59, 0x0
	ml_mov_b32 v57, 0x0
	ml_mov_b32 v56, 0x0
	ml_mov_b32 v54, 0x0
	ml_mov_b32 v2, 0x0
	ml_mov_b32 v3, 0x0
.Ltmp37:
	.loc	1 403 28                        ; generated_attention.py:403:28
	sl_jump BB0_72
BB0_71:                                 ; %._crit_edge63.loopexit
	.loc	1 0 28 is_stmt 0                ; generated_attention.py:0:28
	ml_mov_v2s_b32 s42, v99, 0x3
	ml_mov_v2s_b32 s68, v99, 0x4
	ml_mov_v2s_b32 s69, v99, 0x5
	ml_mov_v2s_b32 s70, v99, 0x6
	ml_mov_v2s_b32 s71, v99, 0x7
	ml_mov_v2s_b32 s72, v99, 0x8
	ml_mov_v2s_b32 s73, v99, 0x9
	ml_mov_v2s_b32 s74, v99, 0xa
	ml_mov_v2s_b32 s75, v99, 0xb
	ml_mov_v2s_b32 s76, v99, 0xc
	ml_mov_v2s_b32 s77, v99, 0xd
	ml_mov_v2s_b32 s78, v99, 0xe
	ml_mov_v2s_b32 s79, v99, 0xf
	ml_mov_v2s_b32 s80, v99, 0x10
	ml_mov_v2s_b32 s81, v99, 0x11
	ml_mov_v2s_b32 s82, v99, 0x12
	ml_mov_v2s_b32 s83, v99, 0x13
	ml_mov_v2s_b32 s37, v99, 0x2
	ml_mov_v2s_b32 s19, v99, 0x14
	ml_mov_v2s_b32 s20, v99, 0x15
	ml_mov_v2s_b32 s98, v99, 0x0
	sl_mov_b32 tcr_lo, s98
	sl_mov_b32 s98, 0xffffffff
	ml_mov_v2s_b32 s98, v99, 0x1
	sl_mov_b32 tcr_hi, s98
	sl_mov_b32 s98, 0xffffffff
BB0_72:                                 ; %._crit_edge63
.Ltmp38:
	.loc	3 315 36 is_stmt 1              ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v34, v59, v53
.Ltmp39:
	.loc	1 318 26                        ; generated_attention.py:318:26
	ml_and_b32 v55, tid, 0x30
	ml_srl_b32 v32, v55, 0x4
	.loc	1 324 56                        ; generated_attention.py:324:56
	ml_add_i32 v35, s37, v32
	ml_mov_b32 v36, 0x1054
	.loc	1 669 44                        ; generated_attention.py:669:44
	ml_mul_u64_u32 v[32:33], s81, v35
	.loc	1 323 52                        ; generated_attention.py:323:52
	sl_add_i32 s6, s20, s42
.Ltmp40:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v41, v57, v53
.Ltmp41:
	.loc	1 326 34                        ; generated_attention.py:326:34
	sl_sra_b32 {s7, wcr}, s6, 0x1f
	ml_mov_b32 v33, 0x5410
	ml_mov_b32 v40, 0x7632
	ml_csel_b32 v37, v33, v36, tcr
	.loc	1 668 42                        ; generated_attention.py:668:42
	sl_mul_u64_u32 s[4:5], s78, s6
	sl_mull_u32 s6, s79, s6
	sl_mull_u32 s7, s78, s7
	sl_add_i32 s5, s5, s7
	sl_add_i32 s5, s5, s6
	.loc	1 673 29                        ; generated_attention.py:673:29
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0x1
.Ltmp42:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v43, v54, v53
.Ltmp43:
	.loc	1 673 29                        ; generated_attention.py:673:29
	sl_add_i64 s[4:5], s[24:25], s[4:5]
.Ltmp44:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(2)
	ml_add_f32 v38, v59, v34
	ml_mov_b32 v34, 0x3276
.Ltmp45:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v39, v38, v52
	ml_csel_b32 v36, v40, v34, tcr
.Ltmp46:
	.loc	1 669 44                        ; generated_attention.py:669:44
	ml_mul_u64_u32 v[33:34], s80, v35
	sl_mov_b32 s17, 0x99
	.loc	1 674 16                        ; generated_attention.py:674:16
	sl_mov_b32 s16, 0x1000504
	.loc	1 324 56                        ; generated_attention.py:324:56
	ml_add_i32 v35, v35, 0x4
.Ltmp47:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(2)
	ml_add_f32 v41, v57, v41
.Ltmp48:
	.loc	1 669 44                        ; generated_attention.py:669:44
	ml_add_i32 v32, v34, v32
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_shl_b32 v44, v33, 0x1
.Ltmp49:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v46, v41, v52
.Ltmp50:
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_shl_b32 v32, v32, 0x1
	ml_srl_b32 v33, v33, 0x1f
	ml_or_b32 v45, v32, v33
	ml_addo_u32 {v32, tcr}, s4, v44
.Ltmp51:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(2)
	ml_add_f32 v43, v54, v43
.Ltmp52:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v49, v43, v52
.Ltmp53:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(2)
	ml_add_f32 v40, v38, v39
.Ltmp54:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v42, v40, v51
.Ltmp55:
	.loc	1 669 44                        ; generated_attention.py:669:44
	ml_mul_u64_u32 v[38:39], s81, v35
.Ltmp56:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v39, v56, v53
.Ltmp57:
	.loc	1 669 44                        ; generated_attention.py:669:44
	ml_mul_u64_u32 v[34:35], s80, v35
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_mov_b32 v53, s5
	ml_addc_i32 v33, v53, v45, tcr
.Ltmp58:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(3)
	ml_add_f32 v41, v41, v46
.Ltmp59:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v54, v41, v51
.Ltmp60:
	.loc	1 669 44                        ; generated_attention.py:669:44
	ml_add_i32 v35, v35, v38
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_shl_b32 v35, v35, 0x1
.Ltmp61:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(3)
	ml_add_f32 v43, v43, v49
	sl_wait lmcnt(2)
	ml_add_f32 v40, v40, v42
.Ltmp62:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v42, v40, v50
.Ltmp63:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(2)
	ml_add_f32 v39, v56, v39
.Ltmp64:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v47, v39, v52
.Ltmp65:
	.loc	1 318 26                        ; generated_attention.py:318:26
	ml_and_b32 v52, tid, 0xf
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_shl_b32 v46, v52, 0x2
	ml_addo_u32 {v32, tcr}, v46, v32
	ml_addc_i32 v33, 0, v33, tcr
.Ltmp66:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(2)
	ml_add_f32 v41, v41, v54
.Ltmp67:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v54, v41, v50
.Ltmp68:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(2)
	ml_add_f32 v40, v40, v42
.Ltmp69:
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ generated_attention.py:543:44 ]
	ml_add_f32 v42, v40, 0x3f800000
.Ltmp70:
	.loc	1 639 20                        ; generated_attention.py:639:20
	ml_rcp_f32 v40, v42
.Ltmp71:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(1)
	ml_add_f32 v38, v39, v47
.Ltmp72:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v39, v38, v51
.Ltmp73:
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_shl_b32 v47, v34, 0x1
	ml_srl_b32 v34, v34, 0x1f
	ml_addo_u32 {v52, tcr}, s4, v47
.Ltmp74:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v51, v43, v51
.Ltmp75:
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_or_b32 v49, v35, v34
	.loc	1 639 20                        ; generated_attention.py:639:20
	ml_xor_b32 v42, v42, 0x80000000
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v35, v53, v49, tcr
	ml_addo_u32 {v34, tcr}, v46, v52
.Ltmp76:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(2)
	ml_add_f32 v41, v41, v54
.Ltmp77:
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v35, 0, v35, tcr
.Ltmp78:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(1)
	ml_add_f32 v38, v38, v39
.Ltmp79:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v39, v38, v50
.Ltmp80:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(1)
	ml_add_f32 v51, v43, v51
.Ltmp81:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ]
	ml_slb_shuffle_rtn_b32 v50, v51, v50
.Ltmp82:
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ generated_attention.py:543:44 ]
	ml_add_f32 v43, v41, 0x3f800000
.Ltmp83:
	.loc	1 639 20                        ; generated_attention.py:639:20
	ml_rcp_f32 v41, v43
	ml_xor_b32 v43, v43, 0x80000000
.Ltmp84:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ generated_attention.py:543:44 ] ] ]
	sl_wait lmcnt(1)
	ml_add_f32 v38, v38, v39
	sl_wait lmcnt(0)
	ml_add_f32 v39, v51, v50
.Ltmp85:
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ generated_attention.py:543:44 ]
	ml_add_f32 v50, v39, 0x3f800000
	ml_add_f32 v51, v38, 0x3f800000
.Ltmp86:
	.loc	1 674 16                        ; generated_attention.py:674:16
	ml_and_b32 v38, tid, 0x1
	ml_cmp_eq_u32 tcr, v38, 0x0
	ml_shl_b32 v38, v48, 0x1
	ml_and_b32 v38, v38, 0xe
	.loc	1 353 12                        ; generated_attention.py:353:12
	ml_and_b32 v39, tid, 0x8
	.loc	1 674 16                        ; generated_attention.py:674:16
	sl_mov_b64 s[4:5], tcr
	ml_srl_b32 v39, v39, 0x3
	ml_anyop3_b32 v38, v38, v39, v55, 0xfffffffe
	sl_mov_b64 tcr, s[2:3]
	ml_xor_b32 v39, v38, 0x1
	sl_cbr_tcraz BB0_74, tcr
; %bb.73:
	.loc	1 0 16 is_stmt 0                ; generated_attention.py:0:16
	ml_mul_f32 v48, v24, v40
	ml_fma_f32 v24, v42, v48, v24
	ml_fma_f32 v24, v24, v40, v48
	ml_mov_b32 v52, 0x99
	ml_cmp_class_f32 tcr, v48, v52
	ml_csel_b32 v24, v48, v24, tcr
	ml_mul_f32 v48, v25, v41
	ml_fma_f32 v25, v43, v48, v25
	ml_fma_f32 v25, v25, v41, v48
	ml_cmp_class_f32 tcr, v48, v52
	ml_csel_b32 v25, v48, v25, tcr
	ml_mul_f32 v48, v28, v40
	ml_fma_f32 v28, v42, v48, v28
	ml_fma_f32 v28, v28, v40, v48
	ml_cmp_class_f32 tcr, v48, v52
	ml_csel_b32 v28, v48, v28, tcr
	ml_mul_f32 v48, v29, v41
	ml_fma_f32 v29, v43, v48, v29
	ml_fma_f32 v29, v29, v41, v48
	ml_cmp_class_f32 tcr, v48, v52
	ml_csel_b32 v29, v48, v29, tcr
	ml_cvt_bf16_f32  v24, v24
	ml_cvt_bf16_f32  v25, v25
	ml_cvt_bf16_f32  v28, v28
	ml_cvt_bf16_f32  v29, v29
	ml_byte_permute_b32 v24, v25, v24, s16
	ml_byte_permute_b32 v25, v29, v28, s16
	sl_mov_b64 tcr, s[4:5]
	ml_csel_b32 v28, v24, v25, tcr
	ml_slb_shuffle_rtn_b32 v28, v28, v38
	ml_csel_b32 v24, v25, v24, tcr
	sl_mov_b32 s6, 0x2010200
	ml_byte_permute_b32 v25, v36, v36, s6
	ml_slb_shuffle_rtn_b32 v24, v24, v39
	ml_byte_permute_b32 v29, v37, v37, s6
	ml_pk_shl_b16 v29, v29, 0x40004
	ml_pk_srl_b8 v29, v29, 0x40004
	ml_pk_shl_b16 v25, v25, 0x40004
	ml_pk_srl_b8 v25, v25, 0x40004
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v29, v28, v24, v29
	.loc	1 674 16                        ; generated_attention.py:674:16
	ml_lsa_store_a64_dword  v[32:33], v29, kop=0
	ml_byte_permute_b32 v24, v28, v24, v25
	ml_lsa_store_a64_dword  v[34:35], v24, kop=0
BB0_74:                                 ; %.critedge
	.loc	1 323 52 is_stmt 1              ; generated_attention.py:323:52
	sl_add_i32 s8, s19, s42
	.loc	1 326 34                        ; generated_attention.py:326:34
	sl_sra_b32 {s6, wcr}, s8, 0x1f
	.loc	1 668 42                        ; generated_attention.py:668:42
	sl_mull_u32 s9, s78, s6
	sl_mul_u64_u32 s[6:7], s78, s8
	sl_add_i32 s7, s7, s9
	sl_mull_u32 s8, s79, s8
	sl_add_i32 s7, s7, s8
	.loc	1 673 29                        ; generated_attention.py:673:29
	sl_shl_b64 {s[6:7], wcr}, s[6:7], 0x1
	sl_add_i64 s[6:7], s[24:25], s[6:7]
	ml_addo_u32 {v24, tcr}, s6, v44
	ml_mov_b32 v28, s7
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	ml_rcp_f32 v44, v51
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v25, v28, v45, tcr
	ml_addo_u32 {v24, tcr}, v46, v24
	.loc	1 0 0                           ; generated_attention.py:0
	ml_rcp_f32 v45, v50
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v25, 0, v25, tcr
	ml_addo_u32 {v29, tcr}, s6, v47
	ml_addc_i32 v47, v28, v49, tcr
	ml_addo_u32 {v28, tcr}, v29, v46
	.loc	1 0 0                           ; generated_attention.py:0
	ml_xor_b32 v46, v51, 0x80000000
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v29, 0, v47, tcr
	.loc	1 674 16 is_stmt 1              ; generated_attention.py:674:16
	sl_mov_b64 tcr, s[0:1]
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	ml_xor_b32 v47, v50, 0x80000000
	.loc	1 674 16                        ; generated_attention.py:674:16
	sl_cbr_tcraz BB0_76, tcr
; %bb.75:
	.loc	1 0 0                           ; generated_attention.py:0
	ml_mul_f32 v48, v26, v44
	ml_mul_f32 v49, v27, v45
	ml_mul_f32 v50, v30, v44
	ml_mul_f32 v51, v31, v45
	ml_fma_f32 v26, v46, v48, v26
	ml_mov_b32 v52, 0x99
	ml_fma_f32 v27, v47, v49, v27
	ml_fma_f32 v30, v46, v50, v30
	ml_fma_f32 v31, v47, v51, v31
	ml_fma_f32 v26, v26, v44, v48
	ml_cmp_class_f32 tcr, v48, v52
	ml_fma_f32 v27, v27, v45, v49
	ml_fma_f32 v30, v30, v44, v50
	ml_fma_f32 v31, v31, v45, v51
	sl_mov_b64 s[6:7], tcr
	ml_cmp_class_f32 tcr, v49, v52
	sl_mov_b64 s[8:9], tcr
	ml_cmp_class_f32 tcr, v50, v52
	sl_mov_b64 s[12:13], tcr
	ml_cmp_class_f32 tcr, v51, v52
	sl_mov_b64 s[14:15], tcr
	sl_mov_b64 tcr, s[6:7]
	ml_csel_b32 v26, v48, v26, tcr
	sl_mov_b64 tcr, s[8:9]
	ml_csel_b32 v27, v49, v27, tcr
	sl_mov_b64 tcr, s[12:13]
	ml_csel_b32 v30, v50, v30, tcr
	sl_mov_b64 tcr, s[14:15]
	ml_csel_b32 v31, v51, v31, tcr
	ml_cvt_bf16_f32  v26, v26
	ml_cvt_bf16_f32  v27, v27
	ml_cvt_bf16_f32  v30, v30
	ml_cvt_bf16_f32  v31, v31
	ml_byte_permute_b32 v26, v27, v26, s16
	ml_byte_permute_b32 v27, v31, v30, s16
	sl_mov_b64 tcr, s[4:5]
	ml_csel_b32 v30, v26, v27, tcr
	ml_slb_shuffle_rtn_b32 v30, v30, v38
	ml_csel_b32 v26, v27, v26, tcr
	.loc	1 674 16                        ; generated_attention.py:674:16
	sl_mov_b32 s6, 0x2010200
	ml_byte_permute_b32 v27, v37, v37, s6
	.loc	1 0 0                           ; generated_attention.py:0
	ml_slb_shuffle_rtn_b32 v26, v26, v39
	.loc	1 674 16                        ; generated_attention.py:674:16
	ml_pk_shl_b16 v27, v27, 0x40004
	ml_pk_srl_b8 v27, v27, 0x40004
	ml_byte_permute_b32 v31, v36, v36, s6
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v27, v30, v26, v27
	ml_lsa_store_a64_dword  v[24:25], v27, kop=0
	ml_pk_shl_b16 v27, v31, 0x40004
	ml_pk_srl_b8 v27, v27, 0x40004
	ml_byte_permute_b32 v26, v30, v26, v27
	ml_lsa_store_a64_dword  v[28:29], v26, kop=0
BB0_76:                                 ; %.critedge2
	sl_mov_b64 tcr, s[2:3]
	sl_cbr_tcraz BB0_78, tcr
; %bb.77:
	.loc	1 0 0                           ; generated_attention.py:0
	ml_mul_f32 v26, v16, v40
	ml_mul_f32 v27, v17, v41
	ml_mul_f32 v30, v20, v40
	ml_mul_f32 v31, v21, v41
	ml_fma_f32 v16, v42, v26, v16
	ml_mov_b32 v48, 0x99
	ml_fma_f32 v17, v43, v27, v17
	ml_fma_f32 v20, v42, v30, v20
	ml_fma_f32 v21, v43, v31, v21
	ml_fma_f32 v16, v16, v40, v26
	ml_cmp_class_f32 tcr, v26, v48
	ml_fma_f32 v17, v17, v41, v27
	ml_fma_f32 v20, v20, v40, v30
	ml_fma_f32 v21, v21, v41, v31
	sl_mov_b64 s[6:7], tcr
	ml_cmp_class_f32 tcr, v27, v48
	sl_mov_b64 s[8:9], tcr
	ml_cmp_class_f32 tcr, v30, v48
	sl_mov_b64 s[12:13], tcr
	ml_cmp_class_f32 tcr, v31, v48
	sl_mov_b64 s[14:15], tcr
	sl_mov_b64 tcr, s[6:7]
	ml_csel_b32 v16, v26, v16, tcr
	sl_mov_b64 tcr, s[8:9]
	ml_csel_b32 v17, v27, v17, tcr
	sl_mov_b64 tcr, s[12:13]
	ml_csel_b32 v20, v30, v20, tcr
	sl_mov_b64 tcr, s[14:15]
	ml_csel_b32 v21, v31, v21, tcr
	ml_cvt_bf16_f32  v16, v16
	ml_cvt_bf16_f32  v17, v17
	ml_cvt_bf16_f32  v20, v20
	ml_cvt_bf16_f32  v21, v21
	ml_byte_permute_b32 v16, v17, v16, s16
	ml_byte_permute_b32 v17, v21, v20, s16
	sl_mov_b64 tcr, s[4:5]
	ml_csel_b32 v20, v16, v17, tcr
	ml_csel_b32 v17, v17, v16, tcr
	ml_slb_shuffle_rtn_b32 v26, v20, v38
	.loc	1 673 29 is_stmt 1              ; generated_attention.py:673:29
	sl_mov_b32 s6, 0x40
	ml_addo_u32 {v16, tcr}, s6, v32
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	ml_slb_shuffle_rtn_b32 v27, v17, v39
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v17, 0, v33, tcr
	ml_addo_u32 {v20, tcr}, s6, v34
	.loc	1 674 16 is_stmt 1              ; generated_attention.py:674:16
	sl_mov_b32 s6, 0x2010200
	ml_byte_permute_b32 v30, v37, v37, s6
	ml_pk_shl_b16 v30, v30, 0x40004
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v21, 0, v35, tcr
	.loc	1 674 16                        ; generated_attention.py:674:16
	ml_pk_srl_b8 v30, v30, 0x40004
	ml_byte_permute_b32 v31, v36, v36, s6
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v30, v26, v27, v30
	ml_lsa_store_a64_dword  v[16:17], v30, kop=0
	ml_pk_shl_b16 v16, v31, 0x40004
	ml_pk_srl_b8 v16, v16, 0x40004
	ml_byte_permute_b32 v16, v26, v27, v16
	ml_lsa_store_a64_dword  v[20:21], v16, kop=0
BB0_78:                                 ; %.critedge4
	sl_mov_b64 tcr, s[0:1]
	sl_cbr_tcraz BB0_80, tcr
; %bb.79:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	ml_mul_f32 v16, v18, v44
	ml_mul_f32 v17, v19, v45
	ml_mul_f32 v20, v22, v44
	ml_mul_f32 v21, v23, v45
	ml_fma_f32 v18, v46, v16, v18
	ml_mov_b32 v26, 0x99
	ml_fma_f32 v19, v47, v17, v19
	ml_fma_f32 v22, v46, v20, v22
	ml_fma_f32 v23, v47, v21, v23
	ml_fma_f32 v18, v18, v44, v16
	ml_cmp_class_f32 tcr, v16, v26
	ml_fma_f32 v19, v19, v45, v17
	ml_fma_f32 v22, v22, v44, v20
	ml_fma_f32 v23, v23, v45, v21
	sl_mov_b64 s[6:7], tcr
	ml_cmp_class_f32 tcr, v17, v26
	sl_mov_b64 s[8:9], tcr
	ml_cmp_class_f32 tcr, v20, v26
	sl_mov_b64 s[12:13], tcr
	ml_cmp_class_f32 tcr, v21, v26
	sl_mov_b64 s[14:15], tcr
	sl_mov_b64 tcr, s[6:7]
	ml_csel_b32 v16, v16, v18, tcr
	sl_mov_b64 tcr, s[8:9]
	ml_csel_b32 v17, v17, v19, tcr
	sl_mov_b64 tcr, s[12:13]
	ml_csel_b32 v18, v20, v22, tcr
	sl_mov_b64 tcr, s[14:15]
	ml_csel_b32 v19, v21, v23, tcr
	ml_cvt_bf16_f32  v16, v16
	ml_cvt_bf16_f32  v17, v17
	ml_cvt_bf16_f32  v18, v18
	ml_cvt_bf16_f32  v19, v19
	ml_byte_permute_b32 v16, v17, v16, s16
	ml_byte_permute_b32 v17, v19, v18, s16
	sl_mov_b64 tcr, s[4:5]
	ml_csel_b32 v18, v16, v17, tcr
	ml_csel_b32 v17, v17, v16, tcr
	ml_slb_shuffle_rtn_b32 v20, v18, v38
	.loc	1 673 29 is_stmt 1              ; generated_attention.py:673:29
	sl_mov_b32 s6, 0x40
	ml_addo_u32 {v16, tcr}, s6, v24
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	ml_slb_shuffle_rtn_b32 v21, v17, v39
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v17, 0, v25, tcr
	ml_addo_u32 {v18, tcr}, s6, v28
	.loc	1 674 16 is_stmt 1              ; generated_attention.py:674:16
	sl_mov_b32 s6, 0x2010200
	ml_byte_permute_b32 v22, v37, v37, s6
	ml_pk_shl_b16 v22, v22, 0x40004
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v19, 0, v29, tcr
	.loc	1 674 16                        ; generated_attention.py:674:16
	ml_pk_srl_b8 v22, v22, 0x40004
	ml_byte_permute_b32 v23, v36, v36, s6
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v22, v20, v21, v22
	ml_lsa_store_a64_dword  v[16:17], v22, kop=0
	ml_pk_shl_b16 v16, v23, 0x40004
	ml_pk_srl_b8 v16, v16, 0x40004
	ml_byte_permute_b32 v16, v20, v21, v16
	ml_lsa_store_a64_dword  v[18:19], v16, kop=0
BB0_80:                                 ; %.critedge6
	sl_mov_b64 tcr, s[2:3]
	sl_cbr_tcraz BB0_82, tcr
; %bb.81:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	ml_mul_f32 v16, v8, v40
	ml_mul_f32 v17, v9, v41
	ml_mul_f32 v18, v12, v40
	ml_mul_f32 v19, v13, v41
	ml_fma_f32 v8, v42, v16, v8
	ml_mov_b32 v20, 0x99
	ml_fma_f32 v9, v43, v17, v9
	ml_fma_f32 v12, v42, v18, v12
	ml_fma_f32 v13, v43, v19, v13
	ml_fma_f32 v8, v8, v40, v16
	ml_cmp_class_f32 tcr, v16, v20
	ml_fma_f32 v9, v9, v41, v17
	ml_fma_f32 v12, v12, v40, v18
	ml_fma_f32 v13, v13, v41, v19
	sl_mov_b64 s[6:7], tcr
	ml_cmp_class_f32 tcr, v17, v20
	sl_mov_b64 s[8:9], tcr
	ml_cmp_class_f32 tcr, v18, v20
	sl_mov_b64 s[12:13], tcr
	ml_cmp_class_f32 tcr, v19, v20
	sl_mov_b64 s[14:15], tcr
	sl_mov_b64 tcr, s[6:7]
	ml_csel_b32 v8, v16, v8, tcr
	sl_mov_b64 tcr, s[8:9]
	ml_csel_b32 v9, v17, v9, tcr
	sl_mov_b64 tcr, s[12:13]
	ml_csel_b32 v12, v18, v12, tcr
	sl_mov_b64 tcr, s[14:15]
	ml_csel_b32 v13, v19, v13, tcr
	ml_cvt_bf16_f32  v8, v8
	ml_cvt_bf16_f32  v9, v9
	ml_cvt_bf16_f32  v12, v12
	ml_cvt_bf16_f32  v13, v13
	ml_byte_permute_b32 v8, v9, v8, s16
	ml_byte_permute_b32 v9, v13, v12, s16
	sl_mov_b64 tcr, s[4:5]
	ml_csel_b32 v12, v8, v9, tcr
	ml_csel_b32 v9, v9, v8, tcr
	ml_slb_shuffle_rtn_b32 v16, v12, v38
	.loc	1 673 29 is_stmt 1              ; generated_attention.py:673:29
	sl_mov_b32 s6, 0x80
	ml_addo_u32 {v8, tcr}, s6, v32
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	ml_slb_shuffle_rtn_b32 v17, v9, v39
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v9, 0, v33, tcr
	ml_addo_u32 {v12, tcr}, s6, v34
	.loc	1 674 16 is_stmt 1              ; generated_attention.py:674:16
	sl_mov_b32 s6, 0x2010200
	ml_byte_permute_b32 v18, v37, v37, s6
	ml_pk_shl_b16 v18, v18, 0x40004
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v13, 0, v35, tcr
	.loc	1 674 16                        ; generated_attention.py:674:16
	ml_pk_srl_b8 v18, v18, 0x40004
	ml_byte_permute_b32 v19, v36, v36, s6
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v18, v16, v17, v18
	ml_lsa_store_a64_dword  v[8:9], v18, kop=0
	ml_pk_shl_b16 v8, v19, 0x40004
	ml_pk_srl_b8 v8, v8, 0x40004
	ml_byte_permute_b32 v8, v16, v17, v8
	ml_lsa_store_a64_dword  v[12:13], v8, kop=0
BB0_82:                                 ; %.critedge8
	sl_mov_b64 tcr, s[0:1]
	sl_cbr_tcraz BB0_84, tcr
; %bb.83:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	ml_mul_f32 v8, v10, v44
	ml_mul_f32 v9, v11, v45
	ml_mul_f32 v12, v14, v44
	ml_mul_f32 v13, v15, v45
	ml_fma_f32 v10, v46, v8, v10
	ml_mov_b32 v16, 0x99
	ml_fma_f32 v11, v47, v9, v11
	ml_fma_f32 v14, v46, v12, v14
	ml_fma_f32 v15, v47, v13, v15
	ml_fma_f32 v10, v10, v44, v8
	ml_cmp_class_f32 tcr, v8, v16
	ml_fma_f32 v11, v11, v45, v9
	ml_fma_f32 v14, v14, v44, v12
	ml_fma_f32 v15, v15, v45, v13
	sl_mov_b64 s[6:7], tcr
	ml_cmp_class_f32 tcr, v9, v16
	sl_mov_b64 s[8:9], tcr
	ml_cmp_class_f32 tcr, v12, v16
	sl_mov_b64 s[12:13], tcr
	ml_cmp_class_f32 tcr, v13, v16
	sl_mov_b64 s[14:15], tcr
	sl_mov_b64 tcr, s[6:7]
	ml_csel_b32 v8, v8, v10, tcr
	sl_mov_b64 tcr, s[8:9]
	ml_csel_b32 v9, v9, v11, tcr
	sl_mov_b64 tcr, s[12:13]
	ml_csel_b32 v10, v12, v14, tcr
	sl_mov_b64 tcr, s[14:15]
	ml_csel_b32 v11, v13, v15, tcr
	ml_cvt_bf16_f32  v8, v8
	ml_cvt_bf16_f32  v9, v9
	ml_cvt_bf16_f32  v10, v10
	ml_cvt_bf16_f32  v11, v11
	ml_byte_permute_b32 v8, v9, v8, s16
	ml_byte_permute_b32 v9, v11, v10, s16
	sl_mov_b64 tcr, s[4:5]
	ml_csel_b32 v10, v8, v9, tcr
	ml_csel_b32 v9, v9, v8, tcr
	ml_slb_shuffle_rtn_b32 v12, v10, v38
	.loc	1 673 29 is_stmt 1              ; generated_attention.py:673:29
	sl_mov_b32 s6, 0x80
	ml_addo_u32 {v8, tcr}, s6, v24
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	ml_slb_shuffle_rtn_b32 v13, v9, v39
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v9, 0, v25, tcr
	ml_addo_u32 {v10, tcr}, s6, v28
	.loc	1 674 16 is_stmt 1              ; generated_attention.py:674:16
	sl_mov_b32 s6, 0x2010200
	ml_byte_permute_b32 v14, v37, v37, s6
	ml_pk_shl_b16 v14, v14, 0x40004
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v11, 0, v29, tcr
	.loc	1 674 16                        ; generated_attention.py:674:16
	ml_pk_srl_b8 v14, v14, 0x40004
	ml_byte_permute_b32 v15, v36, v36, s6
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v14, v12, v13, v14
	ml_lsa_store_a64_dword  v[8:9], v14, kop=0
	ml_pk_shl_b16 v8, v15, 0x40004
	ml_pk_srl_b8 v8, v8, 0x40004
	ml_byte_permute_b32 v8, v12, v13, v8
	ml_lsa_store_a64_dword  v[10:11], v8, kop=0
BB0_84:                                 ; %.critedge10
	sl_mov_b64 tcr, s[2:3]
	sl_cbr_tcraz BB0_86, tcr
; %bb.85:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	ml_mul_f32 v8, v4, v40
	ml_mul_f32 v9, v5, v41
	ml_mul_f32 v10, v1, v41
	ml_mul_f32 v11, v0, v40
	ml_fma_f32 v4, v42, v8, v4
	ml_mov_b32 v12, 0x99
	ml_fma_f32 v5, v43, v9, v5
	ml_fma_f32 v1, v43, v10, v1
	ml_fma_f32 v0, v42, v11, v0
	ml_fma_f32 v4, v4, v40, v8
	ml_cmp_class_f32 tcr, v8, v12
	ml_fma_f32 v5, v5, v41, v9
	ml_fma_f32 v1, v1, v41, v10
	ml_fma_f32 v0, v0, v40, v11
	sl_mov_b64 s[2:3], tcr
	ml_cmp_class_f32 tcr, v9, v12
	sl_mov_b64 s[6:7], tcr
	ml_cmp_class_f32 tcr, v10, v12
	sl_mov_b64 s[8:9], tcr
	ml_cmp_class_f32 tcr, v11, v12
	sl_mov_b64 s[12:13], tcr
	sl_mov_b64 tcr, s[2:3]
	ml_csel_b32 v4, v8, v4, tcr
	sl_mov_b64 tcr, s[6:7]
	ml_csel_b32 v5, v9, v5, tcr
	sl_mov_b64 tcr, s[8:9]
	ml_csel_b32 v1, v10, v1, tcr
	sl_mov_b64 tcr, s[12:13]
	ml_csel_b32 v0, v11, v0, tcr
	ml_cvt_bf16_f32  v4, v4
	ml_cvt_bf16_f32  v5, v5
	ml_cvt_bf16_f32  v0, v0
	ml_cvt_bf16_f32  v1, v1
	ml_byte_permute_b32 v0, v1, v0, s16
	ml_byte_permute_b32 v1, v5, v4, s16
	sl_mov_b64 tcr, s[4:5]
	ml_csel_b32 v4, v1, v0, tcr
	ml_csel_b32 v1, v0, v1, tcr
	ml_slb_shuffle_rtn_b32 v8, v4, v38
	.loc	1 673 29 is_stmt 1              ; generated_attention.py:673:29
	sl_mov_b32 s2, 0xc0
	ml_addo_u32 {v0, tcr}, s2, v32
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	ml_slb_shuffle_rtn_b32 v9, v1, v39
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v1, 0, v33, tcr
	ml_addo_u32 {v4, tcr}, s2, v34
	.loc	1 674 16 is_stmt 1              ; generated_attention.py:674:16
	sl_mov_b32 s2, 0x2010200
	ml_byte_permute_b32 v10, v37, v37, s2
	ml_pk_shl_b16 v10, v10, 0x40004
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v5, 0, v35, tcr
	.loc	1 674 16                        ; generated_attention.py:674:16
	ml_pk_srl_b8 v10, v10, 0x40004
	ml_byte_permute_b32 v11, v36, v36, s2
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v10, v8, v9, v10
	ml_lsa_store_a64_dword  v[0:1], v10, kop=0
	ml_pk_shl_b16 v0, v11, 0x40004
	ml_pk_srl_b8 v0, v0, 0x40004
	ml_byte_permute_b32 v0, v8, v9, v0
	ml_lsa_store_a64_dword  v[4:5], v0, kop=0
BB0_86:                                 ; %.critedge12
	sl_mov_b64 tcr, s[0:1]
	sl_cbr_tcraz BB0_88, tcr
; %bb.87:
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	ml_mul_f32 v0, v6, v44
	ml_mul_f32 v1, v7, v45
	ml_mul_f32 v4, v3, v45
	ml_mul_f32 v5, v2, v44
	ml_fma_f32 v6, v46, v0, v6
	ml_mov_b32 v8, 0x99
	ml_fma_f32 v7, v47, v1, v7
	ml_fma_f32 v3, v47, v4, v3
	ml_fma_f32 v2, v46, v5, v2
	ml_fma_f32 v6, v6, v44, v0
	ml_cmp_class_f32 tcr, v0, v8
	ml_fma_f32 v7, v7, v45, v1
	ml_fma_f32 v3, v3, v45, v4
	ml_fma_f32 v2, v2, v44, v5
	sl_mov_b64 s[0:1], tcr
	ml_cmp_class_f32 tcr, v1, v8
	sl_mov_b64 s[2:3], tcr
	ml_cmp_class_f32 tcr, v4, v8
	sl_mov_b64 s[6:7], tcr
	ml_cmp_class_f32 tcr, v5, v8
	sl_mov_b64 s[8:9], tcr
	sl_mov_b64 tcr, s[0:1]
	ml_csel_b32 v0, v0, v6, tcr
	sl_mov_b64 tcr, s[2:3]
	ml_csel_b32 v1, v1, v7, tcr
	sl_mov_b64 tcr, s[6:7]
	ml_csel_b32 v3, v4, v3, tcr
	sl_mov_b64 tcr, s[8:9]
	ml_csel_b32 v2, v5, v2, tcr
	ml_cvt_bf16_f32  v0, v0
	ml_cvt_bf16_f32  v1, v1
	ml_cvt_bf16_f32  v2, v2
	ml_cvt_bf16_f32  v3, v3
	ml_byte_permute_b32 v2, v3, v2, s16
	ml_byte_permute_b32 v0, v1, v0, s16
	sl_mov_b64 tcr, s[4:5]
	ml_csel_b32 v1, v0, v2, tcr
	ml_csel_b32 v2, v2, v0, tcr
	ml_slb_shuffle_rtn_b32 v4, v1, v38
	.loc	1 673 29 is_stmt 1              ; generated_attention.py:673:29
	sl_mov_b32 s0, 0xc0
	ml_addo_u32 {v0, tcr}, s0, v24
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	ml_slb_shuffle_rtn_b32 v5, v2, v39
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v1, 0, v25, tcr
	ml_addo_u32 {v2, tcr}, s0, v28
	.loc	1 674 16 is_stmt 1              ; generated_attention.py:674:16
	sl_mov_b32 s0, 0x2010200
	ml_byte_permute_b32 v6, v37, v37, s0
	ml_pk_shl_b16 v6, v6, 0x40004
	.loc	1 673 29                        ; generated_attention.py:673:29
	ml_addc_i32 v3, 0, v29, tcr
	.loc	1 674 16                        ; generated_attention.py:674:16
	ml_pk_srl_b8 v6, v6, 0x40004
	ml_byte_permute_b32 v7, v36, v36, s0
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v6, v4, v5, v6
	ml_lsa_store_a64_dword  v[0:1], v6, kop=0
	ml_pk_shl_b16 v0, v7, 0x40004
	ml_pk_srl_b8 v0, v0, 0x40004
	ml_byte_permute_b32 v0, v4, v5, v0
	ml_lsa_store_a64_dword  v[2:3], v0, kop=0
BB0_88:                                 ; %common.ret
	.loc	1 0 0 is_stmt 0                 ; generated_attention.py:0
	sl_eop 
.Ltmp87:
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	kernel_unified_attention.kd
	.type	kernel_unified_attention.kd,@object
	.size	kernel_unified_attention.kd, 64
kernel_unified_attention.kd:
	.asciz	"\000\000\000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	kernel_unified_attention@rel64-kernel_unified_attention.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	537368
	.asciz	"\003\000\264\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	kernel_unified_attention, .Lfunc_end0-kernel_unified_attention
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 17160
; NumSgprs: 104
; NumVgprs: 100
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 12
; VGPRBlocks: 24
; NumSGPRsForWarpsPerNU: 100
; NumVGPRsForWarpsPerNR: 100
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
	.byte	1                               ; DW_CHILDREN_yes
	.byte	49                              ; DW_AT_abstract_origin
	.byte	19                              ; DW_FORM_ref4
	.byte	17                              ; DW_AT_low_pc
	.byte	1                               ; DW_FORM_addr
	.byte	18                              ; DW_AT_high_pc
	.byte	1                               ; DW_FORM_addr
	.byte	88                              ; DW_AT_call_file
	.byte	11                              ; DW_FORM_data1
	.byte	89                              ; DW_AT_call_line
	.byte	5                               ; DW_FORM_data2
	.byte	87                              ; DW_AT_call_column
	.byte	11                              ; DW_FORM_data1
	.byte	0                               ; EOM(1)
	.byte	0                               ; EOM(2)
	.byte	5                               ; Abbreviation Code
	.byte	29                              ; DW_TAG_inlined_subroutine
	.byte	0                               ; DW_CHILDREN_no
	.byte	49                              ; DW_AT_abstract_origin
	.byte	19                              ; DW_FORM_ref4
	.byte	17                              ; DW_AT_low_pc
	.byte	1                               ; DW_FORM_addr
	.byte	18                              ; DW_AT_high_pc
	.byte	1                               ; DW_FORM_addr
	.byte	88                              ; DW_AT_call_file
	.byte	11                              ; DW_FORM_data1
	.byte	89                              ; DW_AT_call_line
	.byte	11                              ; DW_FORM_data1
	.byte	87                              ; DW_AT_call_column
	.byte	11                              ; DW_FORM_data1
	.byte	0                               ; EOM(1)
	.byte	0                               ; EOM(2)
	.byte	6                               ; Abbreviation Code
	.byte	29                              ; DW_TAG_inlined_subroutine
	.byte	1                               ; DW_CHILDREN_yes
	.byte	49                              ; DW_AT_abstract_origin
	.byte	19                              ; DW_FORM_ref4
	.byte	85                              ; DW_AT_ranges
	.byte	6                               ; DW_FORM_data4
	.byte	88                              ; DW_AT_call_file
	.byte	11                              ; DW_FORM_data1
	.byte	89                              ; DW_AT_call_line
	.byte	5                               ; DW_FORM_data2
	.byte	87                              ; DW_AT_call_column
	.byte	11                              ; DW_FORM_data1
	.byte	0                               ; EOM(1)
	.byte	0                               ; EOM(2)
	.byte	7                               ; Abbreviation Code
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
	.byte	8                               ; Abbreviation Code
	.byte	29                              ; DW_TAG_inlined_subroutine
	.byte	0                               ; DW_CHILDREN_no
	.byte	49                              ; DW_AT_abstract_origin
	.byte	19                              ; DW_FORM_ref4
	.byte	85                              ; DW_AT_ranges
	.byte	6                               ; DW_FORM_data4
	.byte	88                              ; DW_AT_call_file
	.byte	11                              ; DW_FORM_data1
	.byte	89                              ; DW_AT_call_line
	.byte	5                               ; DW_FORM_data2
	.byte	87                              ; DW_AT_call_column
	.byte	11                              ; DW_FORM_data1
	.byte	0                               ; EOM(1)
	.byte	0                               ; EOM(2)
	.byte	0                               ; EOM(3)
	.section	.debug_info,"",@progbits
	.long	341                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0x14e DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"generated_attention.py"        ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/workspace/experiments/minicpm-s2/framework/20261022T121701Z-prefill-v-late-gate/source" ; DW_AT_comp_dir
	.byte	0
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.byte	2                               ; Abbrev [2] 0x98:0x1b DW_TAG_subprogram
	.ascii	"kernel_unified_attention"      ; DW_AT_name
	.byte	0
	.byte	1                               ; DW_AT_inline
	.byte	3                               ; Abbrev [3] 0xb3:0xa5 DW_TAG_subprogram
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.long	152                             ; DW_AT_abstract_origin
	.byte	4                               ; Abbrev [4] 0xc8:0x32 DW_TAG_inlined_subroutine
	.long	152                             ; DW_AT_abstract_origin
	.quad	.Ltmp1                          ; DW_AT_low_pc
	.quad	.Ltmp3                          ; DW_AT_high_pc
	.byte	1                               ; DW_AT_call_file
	.short	299                             ; DW_AT_call_line
	.byte	73                              ; DW_AT_call_column
	.byte	5                               ; Abbrev [5] 0xe1:0x18 DW_TAG_inlined_subroutine
	.long	152                             ; DW_AT_abstract_origin
	.quad	.Ltmp1                          ; DW_AT_low_pc
	.quad	.Ltmp2                          ; DW_AT_high_pc
	.byte	2                               ; DW_AT_call_file
	.byte	67                              ; DW_AT_call_line
	.byte	68                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	6                               ; Abbrev [6] 0xfa:0x1a DW_TAG_inlined_subroutine
	.long	152                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges0                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.short	399                             ; DW_AT_call_line
	.byte	8                               ; DW_AT_call_column
	.byte	7                               ; Abbrev [7] 0x107:0xc DW_TAG_inlined_subroutine
	.long	152                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges1                 ; DW_AT_ranges
	.byte	2                               ; DW_AT_call_file
	.byte	193                             ; DW_AT_call_line
	.byte	44                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	6                               ; Abbrev [6] 0x114:0x43 DW_TAG_inlined_subroutine
	.long	152                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges2                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.short	543                             ; DW_AT_call_line
	.byte	44                              ; DW_AT_call_column
	.byte	6                               ; Abbrev [6] 0x121:0x1b DW_TAG_inlined_subroutine
	.long	152                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges3                 ; DW_AT_ranges
	.byte	2                               ; DW_AT_call_file
	.short	413                             ; DW_AT_call_line
	.byte	17                              ; DW_AT_call_column
	.byte	8                               ; Abbrev [8] 0x12e:0xd DW_TAG_inlined_subroutine
	.long	152                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges4                 ; DW_AT_ranges
	.byte	3                               ; DW_AT_call_file
	.short	315                             ; DW_AT_call_line
	.byte	36                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	6                               ; Abbrev [6] 0x13c:0x1a DW_TAG_inlined_subroutine
	.long	152                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges5                 ; DW_AT_ranges
	.byte	2                               ; DW_AT_call_file
	.short	406                             ; DW_AT_call_line
	.byte	31                              ; DW_AT_call_column
	.byte	7                               ; Abbrev [7] 0x149:0xc DW_TAG_inlined_subroutine
	.long	152                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges5                 ; DW_AT_ranges
	.byte	3                               ; DW_AT_call_file
	.byte	213                             ; DW_AT_call_line
	.byte	40                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	0                               ; End Of Children Mark
	.byte	0                               ; End Of Children Mark
	.byte	0                               ; End Of Children Mark
	.section	.debug_ranges,"",@progbits
.Ldebug_ranges0:
	.quad	.Ltmp4-.Lfunc_begin0
	.quad	.Ltmp5-.Lfunc_begin0
	.quad	.Ltmp6-.Lfunc_begin0
	.quad	.Ltmp8-.Lfunc_begin0
	.quad	.Ltmp9-.Lfunc_begin0
	.quad	.Ltmp10-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges1:
	.quad	.Ltmp7-.Lfunc_begin0
	.quad	.Ltmp8-.Lfunc_begin0
	.quad	.Ltmp9-.Lfunc_begin0
	.quad	.Ltmp10-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges2:
	.quad	.Ltmp11-.Lfunc_begin0
	.quad	.Ltmp21-.Lfunc_begin0
	.quad	.Ltmp22-.Lfunc_begin0
	.quad	.Ltmp23-.Lfunc_begin0
	.quad	.Ltmp24-.Lfunc_begin0
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
	.quad	.Ltmp46-.Lfunc_begin0
	.quad	.Ltmp47-.Lfunc_begin0
	.quad	.Ltmp48-.Lfunc_begin0
	.quad	.Ltmp49-.Lfunc_begin0
	.quad	.Ltmp50-.Lfunc_begin0
	.quad	.Ltmp51-.Lfunc_begin0
	.quad	.Ltmp55-.Lfunc_begin0
	.quad	.Ltmp56-.Lfunc_begin0
	.quad	.Ltmp57-.Lfunc_begin0
	.quad	.Ltmp58-.Lfunc_begin0
	.quad	.Ltmp60-.Lfunc_begin0
	.quad	.Ltmp61-.Lfunc_begin0
	.quad	.Ltmp65-.Lfunc_begin0
	.quad	.Ltmp66-.Lfunc_begin0
	.quad	.Ltmp70-.Lfunc_begin0
	.quad	.Ltmp71-.Lfunc_begin0
	.quad	.Ltmp73-.Lfunc_begin0
	.quad	.Ltmp74-.Lfunc_begin0
	.quad	.Ltmp75-.Lfunc_begin0
	.quad	.Ltmp76-.Lfunc_begin0
	.quad	.Ltmp77-.Lfunc_begin0
	.quad	.Ltmp78-.Lfunc_begin0
	.quad	.Ltmp83-.Lfunc_begin0
	.quad	.Ltmp84-.Lfunc_begin0
	.quad	.Ltmp86-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges3:
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
	.quad	.Ltmp25-.Lfunc_begin0
	.quad	.Ltmp26-.Lfunc_begin0
	.quad	.Ltmp36-.Lfunc_begin0
	.quad	.Ltmp37-.Lfunc_begin0
	.quad	.Ltmp38-.Lfunc_begin0
	.quad	.Ltmp39-.Lfunc_begin0
	.quad	.Ltmp40-.Lfunc_begin0
	.quad	.Ltmp41-.Lfunc_begin0
	.quad	.Ltmp42-.Lfunc_begin0
	.quad	.Ltmp43-.Lfunc_begin0
	.quad	.Ltmp44-.Lfunc_begin0
	.quad	.Ltmp46-.Lfunc_begin0
	.quad	.Ltmp47-.Lfunc_begin0
	.quad	.Ltmp48-.Lfunc_begin0
	.quad	.Ltmp49-.Lfunc_begin0
	.quad	.Ltmp50-.Lfunc_begin0
	.quad	.Ltmp51-.Lfunc_begin0
	.quad	.Ltmp55-.Lfunc_begin0
	.quad	.Ltmp56-.Lfunc_begin0
	.quad	.Ltmp57-.Lfunc_begin0
	.quad	.Ltmp58-.Lfunc_begin0
	.quad	.Ltmp60-.Lfunc_begin0
	.quad	.Ltmp61-.Lfunc_begin0
	.quad	.Ltmp65-.Lfunc_begin0
	.quad	.Ltmp66-.Lfunc_begin0
	.quad	.Ltmp69-.Lfunc_begin0
	.quad	.Ltmp71-.Lfunc_begin0
	.quad	.Ltmp73-.Lfunc_begin0
	.quad	.Ltmp74-.Lfunc_begin0
	.quad	.Ltmp75-.Lfunc_begin0
	.quad	.Ltmp76-.Lfunc_begin0
	.quad	.Ltmp77-.Lfunc_begin0
	.quad	.Ltmp78-.Lfunc_begin0
	.quad	.Ltmp82-.Lfunc_begin0
	.quad	.Ltmp84-.Lfunc_begin0
	.quad	.Ltmp85-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges4:
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
	.quad	.Ltmp25-.Lfunc_begin0
	.quad	.Ltmp26-.Lfunc_begin0
	.quad	.Ltmp44-.Lfunc_begin0
	.quad	.Ltmp45-.Lfunc_begin0
	.quad	.Ltmp47-.Lfunc_begin0
	.quad	.Ltmp48-.Lfunc_begin0
	.quad	.Ltmp51-.Lfunc_begin0
	.quad	.Ltmp52-.Lfunc_begin0
	.quad	.Ltmp53-.Lfunc_begin0
	.quad	.Ltmp54-.Lfunc_begin0
	.quad	.Ltmp58-.Lfunc_begin0
	.quad	.Ltmp59-.Lfunc_begin0
	.quad	.Ltmp61-.Lfunc_begin0
	.quad	.Ltmp62-.Lfunc_begin0
	.quad	.Ltmp63-.Lfunc_begin0
	.quad	.Ltmp64-.Lfunc_begin0
	.quad	.Ltmp66-.Lfunc_begin0
	.quad	.Ltmp67-.Lfunc_begin0
	.quad	.Ltmp68-.Lfunc_begin0
	.quad	.Ltmp69-.Lfunc_begin0
	.quad	.Ltmp71-.Lfunc_begin0
	.quad	.Ltmp72-.Lfunc_begin0
	.quad	.Ltmp76-.Lfunc_begin0
	.quad	.Ltmp77-.Lfunc_begin0
	.quad	.Ltmp78-.Lfunc_begin0
	.quad	.Ltmp79-.Lfunc_begin0
	.quad	.Ltmp80-.Lfunc_begin0
	.quad	.Ltmp81-.Lfunc_begin0
	.quad	.Ltmp84-.Lfunc_begin0
	.quad	.Ltmp85-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges5:
	.quad	.Ltmp28-.Lfunc_begin0
	.quad	.Ltmp29-.Lfunc_begin0
	.quad	.Ltmp30-.Lfunc_begin0
	.quad	.Ltmp31-.Lfunc_begin0
	.quad	.Ltmp32-.Lfunc_begin0
	.quad	.Ltmp33-.Lfunc_begin0
	.quad	.Ltmp34-.Lfunc_begin0
	.quad	.Ltmp35-.Lfunc_begin0
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
      - .name:           KArg_6
        .offset:         48
        .size:           4
        .value_kind:     by_value
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
      - .name:           KArg_9
        .offset:         72
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_10
        .offset:         76
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_11
        .offset:         80
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_12
        .offset:         88
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_13
        .offset:         96
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_14
        .offset:         104
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_15
        .offset:         112
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_16
        .offset:         120
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_17
        .offset:         128
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_18
        .offset:         136
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_19
        .offset:         144
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_20
        .offset:         152
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_21
        .offset:         160
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_22
        .offset:         168
        .size:           8
        .value_kind:     by_value
      - .address_space:  global
        .name:           KArg_23
        .offset:         176
        .size:           8
        .value_kind:     global_buffer
      - .name:           KArg_24
        .offset:         184
        .size:           4
        .value_kind:     by_value
      - .address_space:  global
        .name:           KArg_25
        .offset:         192
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_26
        .offset:         200
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_27
        .offset:         208
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_28
        .offset:         216
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_29
        .offset:         224
        .size:           8
        .value_kind:     global_buffer
      - .name:           KArg_30
        .offset:         232
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_31
        .offset:         240
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_32
        .offset:         248
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_33
        .offset:         256
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_34
        .offset:         264
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_35
        .offset:         272
        .size:           8
        .value_kind:     by_value
      - .address_space:  global
        .name:           KArg_36
        .offset:         280
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_37
        .offset:         288
        .size:           8
        .value_kind:     global_buffer
    .group_segment_fixed_size: 0
    .kernarg_segment_align: 8
    .kernarg_segment_size: 296
    .max_flat_workgroup_size: 0
    .name:           kernel_unified_attention
    .private_segment_fixed_size: 0
    .sgpr_count:     104
    .sgpr_spill_count: 22
    .symbol:         kernel_unified_attention.kd
    .vgpr_count:     100
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
