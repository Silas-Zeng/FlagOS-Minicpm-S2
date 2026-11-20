	.text
	.globl	head_temperature_kernel         ; -- Begin function head_temperature_kernel
	.p2align	3
	.type	head_temperature_kernel,@function
	.iluvatar_kernel head_temperature_kernel
head_temperature_kernel:                ; @head_temperature_kernel
.Lfunc_begin0:
	.file	1 "/workspace/experiments/minicpm-s2/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/source" "candidate.py"
	.loc	1 6 0                           ; candidate.py:6:0
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
		granulated_workitem_vgpr_count = 5
		granulated_warp_sgpr_count = 6
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
		kernarg_segment_byte_size = 88
		workgroup_fbarrier_count = 0
		warp_sgpr_count = 49
		workitem_vgpr_count = 21
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
	sl_mov_b32 s44, tcr_lo
	ml_vrf_init_u32 v4, tcr
.Ltmp0:
	.file	2 "/usr/local/lib/python3.12/site-packages/triton/language" "standard.py"
	.loc	2 65 17 prologue_end            ; standard.py:65:17 @[ candidate.py:33:24 ]
	sl_lsa_load_b32x16 s[12:27], s[4:5], noreg, #0, ca
	sl_lsa_load_b32x16 s[28:43], s[4:5], noreg, #64, ca
.Ltmp1:
	.loc	2 65 17 is_stmt 0               ; standard.py:65:17 @[ candidate.py:32:24 ]
	sl_wait smcnt(0)
	sl_add_i32 s0, s20, 0x1f
.Ltmp2:
	.loc	2 65 17                         ; standard.py:65:17 @[ candidate.py:33:24 ]
	sl_add_i32 s1, s21, 0x3f
.Ltmp3:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:32:24 ]
	sl_sra_b32 {s2, wcr}, s0, 0x1f
.Ltmp4:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:33:24 ]
	sl_sra_b32 {s3, wcr}, s1, 0x1f
.Ltmp5:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:32:24 ]
	sl_srl_b32 {s2, wcr}, s2, 0x1b
.Ltmp6:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:33:24 ]
	sl_srl_b32 {s3, wcr}, s3, 0x1a
.Ltmp7:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:32:24 ]
	sl_add_i32 s0, s0, s2
.Ltmp8:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:33:24 ]
	sl_add_i32 s1, s1, s3
.Ltmp9:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:32:24 ]
	sl_sra_b32 {s16, wcr}, s0, 0x5
.Ltmp10:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:33:24 ]
	sl_sra_b32 {s0, wcr}, s1, 0x6
.Ltmp11:
	.loc	1 35 22 is_stmt 1               ; candidate.py:35:22
	sl_sra_b32 {s17, wcr}, s1, 0x1f
	sl_shl_b32 {s26, wcr}, s0, 0x3
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_abs_i32 s1, s26
	ml_cvt_f32_u32  v0, s1
	sl_reg_read s2, hwreg(HW_REG_MODE)
	ml_rcp_f32 v0, v0
	sl_or_b32 {s3, wcr}, s2, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s3
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s2
	ml_mov_v2s_b32 s4, v0, 0x0
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
	sl_sub_bi_u64 s[8:9], s[10:11], s[10:11], wcr
	sl_and_b64 {s[4:5], wcr}, s[4:5], s[8:9]
	sl_mov_b32 s2, 0xffffffff
	sl_or_b32 {s4, wcr}, s4, s5
	sl_csel_b32 s4, s2, 0x0, wcr
	sl_cmp_eq_u32 wcr, s4, 0x0
	sl_add_i32 s4, s3, 0x1
	sl_add_i32 s5, s3, 0xffffffff
	sl_csel_b32 s3, s3, s4, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s3, s5, wcr
	sl_xor_b32 {s1, wcr}, s1, s17
	sl_sub_i32 s1, s1, s17
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s3, s1, 0xffffffff, wcr
	.loc	1 36 41                         ; candidate.py:36:41
	sl_mull_u32 s17, s3, 0x8
	.loc	1 36 30 is_stmt 0               ; candidate.py:36:30
	sl_sub_i32 s0, s16, s17
	.loc	1 36 50                         ; candidate.py:36:50
	sl_min_i32 s16, s0, 0x8
	.loc	1 37 40 is_stmt 1               ; candidate.py:37:40
	sl_abs_i32 s27, s16
	ml_cvt_f32_u32  v0, s27
	sl_reg_read s1, hwreg(HW_REG_MODE)
	ml_rcp_f32 v0, v0
	sl_cmp_eq_u32 wcr, s16, 0x0
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_or_b32 {s4, wcr}, s1, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s4
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s1
	.loc	1 41 40                         ; candidate.py:41:40
	ml_mov_b32 v5, tid
	.loc	1 37 40                         ; candidate.py:37:40
	ml_mov_v2s_b32 s1, v0, 0x0
	ml_mov_b32 v6, 0x0
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v2, 0x0
	sl_mul_u64_u32 s[4:5], s1, s27
	sl_neg_i32 s8, s4
	sl_cmp_eq_u32 wcr, s5, 0x0
	sl_csel_b32 s4, s8, s4, wcr
	sl_mul_u64_u32 s[4:5], s4, s1
	sl_add_i32 s4, s1, s5
	sl_sub_i32 s1, s1, s5
	sl_csel_b32 s30, s4, s1, wcr
	sl_mul_u64_u32 s[4:5], s30, s6
	sl_mull_u32 s1, s5, s27
	sl_sub_i32 s31, s6, s1
	sl_cmp_ge_u32 wcr, s31, s27
	sl_sub_bi_u64 s[4:5], s[10:11], s[10:11], wcr
	sl_cmp_ge_u32 wcr, s6, s1
	sl_sub_bi_u32 s1, s10, s10, wcr
	sl_sub_bi_u64 s[8:9], s[10:11], s[10:11], wcr
	sl_and_b64 {s[4:5], wcr}, s[4:5], s[8:9]
	sl_or_b32 {s4, wcr}, s4, s5
	sl_csel_b32 s4, s2, 0x0, wcr
	sl_cmp_eq_u32 wcr, s4, 0x0
	sl_sub_i32 s4, s31, s27
	sl_add_i32 s5, s31, s27
	sl_csel_b32 s4, s31, s4, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s4, s5, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s1, s2, s1, wcr
	.loc	1 37 34 is_stmt 0               ; candidate.py:37:34
	sl_add_i32 s31, s17, s1
	.loc	1 38 19 is_stmt 1               ; candidate.py:38:19
	sl_mull_u32 s1, s3, s26
	sl_sub_i32 s1, s6, s1
	.loc	1 38 29 is_stmt 0               ; candidate.py:38:29
	sl_xor_b32 {s3, wcr}, s1, s16
	sl_sra_b32 {s3, wcr}, s3, 0x1f
	sl_abs_i32 s1, s1
	sl_mul_u64_u32 s[4:5], s30, s1
	sl_mull_u32 s4, s5, s27
	sl_sub_i32 s6, s1, s4
	sl_cmp_ge_u32 wcr, s6, s27
	sl_sub_bi_u64 s[8:9], s[10:11], s[10:11], wcr
	sl_cmp_ge_u32 wcr, s1, s4
	sl_sub_bi_u32 s1, s10, s10, wcr
	sl_sub_bi_u64 s[16:17], s[10:11], s[10:11], wcr
	sl_and_b64 {s[8:9], wcr}, s[8:9], s[16:17]
	sl_or_b32 {s8, wcr}, s8, s9
	sl_csel_b32 s4, s2, 0x0, wcr
	sl_cmp_eq_u32 wcr, s4, 0x0
	sl_add_i32 s4, s5, 0x1
	sl_add_i32 s6, s5, 0xffffffff
	sl_csel_b32 s4, s5, s4, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s4, s6, wcr
	sl_xor_b32 {s1, wcr}, s1, s3
	sl_sub_i32 s1, s1, s3
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s2, s1, wcr
	.loc	1 40 17 is_stmt 1               ; candidate.py:40:17
	sl_mull_u32 s27, s31, 0x20
	.loc	1 40 40 is_stmt 0               ; candidate.py:40:40
	sl_bfe2_b32 s30, tcr_lo, 0x66
	.loc	1 41 17 is_stmt 1               ; candidate.py:41:17
	sl_mull_u32 s26, s0, 0x40
.Ltmp12:
	.loc	2 65 17                         ; standard.py:65:17 @[ candidate.py:51:37 ]
	sl_add_i32 s0, s22, 0x3f
.Ltmp13:
	.loc	1 51 26                         ; candidate.py:51:26
	sl_cmp_gt_i32 wcr, s0, 0x3f
	ml_mov_b32 v1, 0x0
	sl_cbr_wcrz BB0_6, wcr
; %bb.1:                                ; %.lr.ph
.Ltmp14:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:51:37 ]
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_srl_b32 {s1, wcr}, s1, 0x1a
.Ltmp15:
	.loc	1 43 48                         ; candidate.py:43:48
	sl_abs_i32 s3, s21
	ml_cvt_f32_u32  v0, s3
.Ltmp16:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:51:37 ]
	sl_add_i32 s0, s0, s1
.Ltmp17:
	.loc	1 43 48                         ; candidate.py:43:48
	ml_rcp_f32 v0, v0
.Ltmp18:
	.loc	2 65 30                         ; standard.py:65:30 @[ candidate.py:51:37 ]
	sl_sra_b32 {s22, wcr}, s0, 0x6
.Ltmp19:
	.loc	1 43 48                         ; candidate.py:43:48
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_sra_b32 {s6, wcr}, s26, 0x1f
	sl_abs_i32 s8, s26
	sl_or_b32 {s1, wcr}, s0, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s0
	ml_mov_v2s_b32 s4, v0, 0x0
	.loc	1 42 48                         ; candidate.py:42:48
	sl_abs_i32 s16, s20
	ml_cvt_f32_u32  v0, s16
	.loc	1 43 48                         ; candidate.py:43:48
	sl_mul_u64_u32 s[0:1], s4, s3
	sl_neg_i32 s5, s0
	sl_cmp_eq_u32 wcr, s1, 0x0
	sl_csel_b32 s0, s5, s0, wcr
	sl_mul_u64_u32 s[0:1], s0, s4
	sl_add_i32 s0, s4, s1
	sl_sub_i32 s1, s4, s1
	sl_csel_b32 s0, s0, s1, wcr
	sl_mul_u64_u32 s[0:1], s0, s8
	sl_mull_u32 s0, s1, s3
	sl_sub_i32 s1, s8, s0
	sl_cmp_ge_u32 wcr, s1, s3
	sl_sub_bi_u64 s[4:5], s[10:11], s[10:11], wcr
	sl_cmp_ge_u32 wcr, s8, s0
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_sub_bi_u64 s[8:9], s[10:11], s[10:11], wcr
	sl_and_b64 {s[4:5], wcr}, s[4:5], s[8:9]
	sl_or_b32 {s4, wcr}, s4, s5
	sl_csel_b32 s4, s2, 0x0, wcr
	sl_cmp_eq_u32 wcr, s4, 0x0
	sl_sub_i32 s4, s1, s3
	sl_add_i32 s3, s1, s3
	sl_csel_b32 s1, s1, s4, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s1, s3, wcr
	sl_xor_b32 {s0, wcr}, s0, s6
	sl_sub_i32 s0, s0, s6
	sl_cmp_ne_u32 wcr, s21, 0x0
	sl_csel_b32 s0, s0, 0xffffffff, wcr
	.loc	1 47 63                         ; candidate.py:47:63
	sl_mull_u32 s0, s0, s24
	.loc	1 44 17                         ; candidate.py:44:17
	sl_mull_u32 s3, s7, 0x40
	.loc	1 47 48                         ; candidate.py:47:48
	sl_add_i32 s4, s0, s3
	.loc	1 42 48                         ; candidate.py:42:48
	ml_rcp_f32 v0, v0
	.loc	1 47 22                         ; candidate.py:47:22
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	.loc	1 42 48                         ; candidate.py:42:48
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_sra_b32 {s17, wcr}, s27, 0x1f
	sl_abs_i32 s8, s27
	sl_or_b32 {s1, wcr}, s0, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s0
	ml_mov_v2s_b32 s6, v0, 0x0
	ml_shl_b32 v0, tid, 0x2
	ml_mov_b32 v3, 0x0
	sl_mul_u64_u32 s[0:1], s6, s16
	sl_neg_i32 s7, s0
	sl_cmp_eq_u32 wcr, s1, 0x0
	sl_csel_b32 s0, s7, s0, wcr
	sl_mul_u64_u32 s[0:1], s0, s6
	sl_add_i32 s0, s6, s1
	sl_sub_i32 s1, s6, s1
	sl_csel_b32 s0, s0, s1, wcr
	sl_mul_u64_u32 s[0:1], s0, s8
	sl_mull_u32 s0, s1, s16
	sl_sub_i32 s1, s8, s0
	sl_cmp_ge_u32 wcr, s1, s16
	sl_sub_bi_u64 s[6:7], s[10:11], s[10:11], wcr
	sl_cmp_ge_u32 wcr, s8, s0
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_sub_bi_u64 s[8:9], s[10:11], s[10:11], wcr
	sl_and_b64 {s[6:7], wcr}, s[6:7], s[8:9]
	sl_or_b32 {s6, wcr}, s6, s7
	sl_csel_b32 s6, s2, 0x0, wcr
	sl_cmp_eq_u32 wcr, s6, 0x0
	sl_sub_i32 s6, s1, s16
	sl_add_i32 s7, s1, s16
	sl_csel_b32 s1, s1, s6, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s1, s7, wcr
	sl_xor_b32 {s0, wcr}, s0, s17
	sl_sub_i32 s0, s0, s17
	sl_cmp_ne_u32 wcr, s20, 0x0
	sl_csel_b32 s0, s0, 0xffffffff, wcr
	.loc	1 46 36                         ; candidate.py:46:36
	sl_mull_u32 s0, s0, s23
	.loc	1 46 48 is_stmt 0               ; candidate.py:46:48
	sl_add_i32 s32, s0, s3
	.loc	1 46 21                         ; candidate.py:46:21
	sl_sra_b32 {s33, wcr}, s32, 0x1f
	sl_bfe2_b32 s0, s44, 0x26
	sl_srl_b32 {s1, wcr}, s30, 0x1
	sl_mull_u32 s7, s23, 0x2
	sl_mull_u32 s3, s0, 0x800
	sl_mull_u32 s6, s1, 0x400
	sl_add_i32 s9, s3, s6
	sl_mull_u32 s3, s1, 0x40
	sl_mull_u32 s6, s0, s23
	sl_mull_u32 s6, s6, 0x20
	sl_add_i32 s8, s6, s3
	sl_mull_u32 s3, s24, 0x2
	sl_mull_u32 s6, s0, 0x400
	sl_mull_u32 s16, s1, 0x800
	sl_add_i32 s17, s6, s16
	sl_mull_u32 s0, s0, 0x40
	sl_mull_u32 s1, s1, s24
	sl_mull_u32 s1, s1, 0x20
	sl_add_i32 s16, s1, s0
	sl_mull_u32 s0, s44, 0x8
	sl_and_b32 {s23, wcr}, s0, 0x800
	ml_add_i32 v1, s23, v0
	ml_xor_b32 v6, v1, 0x80
	ml_shl_b32 v1, v4, 0x6
	ml_and_b32 v1, v1, 0x300
	sl_mull_u32 s0, s44, 0x20
	sl_and_b32 {s0, wcr}, s0, 0x1800
	ml_anyop3_b32 v7, s0, v1, v0, 0xfffffffe
	ml_xor_b32 v8, v7, 0x10
	ml_xor_b32 v9, v7, 0x20
	ml_xor_b32 v10, v7, 0x30
	.loc	1 51 26 is_stmt 1               ; candidate.py:51:26
	sl_shl_b64 {s[0:1], wcr}, s[4:5], 0x1
	sl_add_i64 s[0:1], s[14:15], s[0:1]
	sl_shl_b64 {s[4:5], wcr}, s[32:33], 0x1
	sl_add_i64 s[4:5], s[12:13], s[4:5]
	ml_mov_b32 v0, 0x0
	sl_mov_b32 s12, 0x2000
	sl_mov_b32 s13, 0x2400
	sl_mov_b32 s14, 0x400
	ml_mov_b32 v1, 0x0
	sl_jump BB0_3
BB0_2:                                  ;   in Loop: Header=BB0_3 Depth=1
	.loc	1 52 24                         ; candidate.py:52:24
	sl_wait g2scnt(0)
	.loc	1 53 24                         ; candidate.py:53:24
	sl_sme_load_16x1b64_col s[0:3], s[16:17], 0x0, 0x0, 0x0, 0x1
	sl_wait g2scnt(0)
	.loc	1 52 24                         ; candidate.py:52:24
	sl_barrier 
	sl_add_i32 s6, s23, 0x2000
	ml_slb_blkload_x1  v11, noreg, s6, #0, null
	sl_add_i32 s15, s23, 0x2400
	.loc	1 51 26                         ; candidate.py:51:26
	sl_add_i64 s[0:1], s[0:1], 0x80
	sl_add_i32 s22, s22, 0xffffffff
	.loc	1 52 24                         ; candidate.py:52:24
	ml_slb_blkload_x1  v12, noreg, s6, #256, null
	.loc	1 51 26                         ; candidate.py:51:26
	sl_cmp_eq_u32 wcr, s22, 0x0
	sl_add_i64 s[4:5], s[4:5], 0x80
	.loc	1 52 24                         ; candidate.py:52:24
	ml_slb_blkload_x1  v13, noreg, s15, #0, null
	ml_slb_blkload_x1  v14, noreg, s15, #256, null
	ml_slb_load_b32x1  v15, v6, s12, #512, null
	.loc	1 53 24                         ; candidate.py:53:24
	ml_slb_load_b32x1  v17, v7, noreg, #0, null
	ml_slb_load_b32x1  v18, v8, noreg, #0, null
	.loc	1 52 24                         ; candidate.py:52:24
	ml_slb_load_b32x1  v16, v6, s12, #768, null
	.loc	1 53 24                         ; candidate.py:53:24
	ml_slb_load_b32x1  v19, v9, noreg, #0, null
	ml_slb_load_b32x1  v20, v10, noreg, #0, null
	.loc	1 54 29                         ; candidate.py:54:29
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[11:12], v[17:18], v[0:3]
	.loc	1 52 24                         ; candidate.py:52:24
	ml_slb_load_b32x1  v11, v6, s13, #512, null
	.loc	1 53 24                         ; candidate.py:53:24
	ml_slb_load_b32x1  v17, v7, s14, #0, null
	ml_slb_load_b32x1  v18, v8, s14, #0, null
	.loc	1 54 29                         ; candidate.py:54:29
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[15:16], v[19:20], v[0:3]
	.loc	1 52 24                         ; candidate.py:52:24
	ml_slb_load_b32x1  v12, v6, s13, #768, null
	.loc	1 53 24                         ; candidate.py:53:24
	ml_slb_load_b32x1  v15, v9, s14, #0, null
	ml_slb_load_b32x1  v16, v10, s14, #0, null
	.loc	1 54 29                         ; candidate.py:54:29
	sl_wait lmcnt(3)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[13:14], v[17:18], v[0:3]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[11:12], v[15:16], v[0:3]
	.loc	1 51 26                         ; candidate.py:51:26
	sl_cbr_wcrnz BB0_5, wcr
BB0_3:                                  ; =>This Inner Loop Header: Depth=1
	.loc	1 52 24                         ; candidate.py:52:24
	sl_wait lmcnt(0) g2scnt(0)
	sl_barrier_req 0x0
	sl_barrier_wait 0x0
	sl_cmp_lt_u32 wcr, s30, 0x4
	sl_cbr_wcrz BB0_2, wcr
; %bb.4:                                ;   in Loop: Header=BB0_3 Depth=1
	.loc	1 0 24 is_stmt 0                ; candidate.py:0:24
	sl_mov_b32 s6, s2
	.loc	1 52 24                         ; candidate.py:52:24
	sl_sme_load_16x1b64_rowxfb16 s[4:7], s[8:9], 0x0, 0x0, 0x800, 0x1
	sl_jump BB0_2
BB0_5:                                  ; %._crit_edge.loopexit
	.loc	1 82 24 is_stmt 1               ; candidate.py:82:24
	ml_cvt_bf16_f32  v6, v0
	ml_cvt_bf16_f32  v0, v1
	ml_cvt_bf16_f32  v2, v2
	ml_cvt_bf16_f32  v1, v3
BB0_6:                                  ; %._crit_edge
	.loc	1 40 27                         ; candidate.py:40:27
	sl_add_i32 s8, s27, s30
	.loc	1 79 17                         ; candidate.py:79:17
	sl_cmp_lt_i32 wcr, s8, s20
	sl_sub_bi_u64 s[12:13], s[10:11], s[10:11], wcr
	sl_sub_bi_u32 s0, s10, s10, wcr
	.loc	1 81 48                         ; candidate.py:81:48
	sl_sra_b32 {s9, wcr}, s8, 0x1f
	sl_shl_b64 {s[4:5], wcr}, s[8:9], 0x2
	sl_add_i64 s[4:5], s[28:29], s[4:5]
	sl_mov_b32 s7, s2
	sl_mov_b32 s9, 0x3f800000
	.loc	1 81 30 is_stmt 0               ; candidate.py:81:30
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_mov_b32 s22, 0x3f800000
	sl_cbr_wcrz BB0_8, wcr
; %bb.7:
	ml_lsa_load_dword v3, s[4:7], noreg, noreg, #0, ca
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s22, v3, 0x0
BB0_8:
	.loc	1 40 27 is_stmt 1               ; candidate.py:40:27
	sl_add_i32 s23, s8, 0x8
	.loc	1 79 17                         ; candidate.py:79:17
	sl_cmp_lt_i32 wcr, s23, s20
	sl_sub_bi_u64 s[14:15], s[10:11], s[10:11], wcr
	.loc	1 81 30                         ; candidate.py:81:30
	sl_cbr_wcrz BB0_10, wcr
; %bb.9:
	ml_lsa_load_dword v3, s[4:7], noreg, noreg, #32, ca
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s9, v3, 0x0
BB0_10:
	.loc	1 40 27                         ; candidate.py:40:27
	sl_add_i32 s24, s8, 0x10
	.loc	1 79 17                         ; candidate.py:79:17
	sl_cmp_lt_i32 wcr, s24, s20
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	sl_mov_b32 s16, 0x3f800000
	sl_mov_b32 s17, 0x3f800000
	.loc	1 81 30                         ; candidate.py:81:30
	sl_cbr_wcrz BB0_12, wcr
; %bb.11:
	ml_lsa_load_dword v3, s[4:7], noreg, noreg, #64, ca
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s17, v3, 0x0
BB0_12:
	.loc	1 40 27                         ; candidate.py:40:27
	sl_add_i32 s27, s8, 0x18
	.loc	1 79 17                         ; candidate.py:79:17
	sl_cmp_lt_i32 wcr, s27, s20
	sl_sub_bi_u64 s[0:1], s[10:11], s[10:11], wcr
	.loc	1 81 30                         ; candidate.py:81:30
	sl_cbr_wcrz BB0_14, wcr
; %bb.13:
	ml_lsa_load_dword v3, s[4:7], noreg, noreg, #96, ca
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s16, v3, 0x0
BB0_14:
	.loc	1 41 27                         ; candidate.py:41:27
	ml_add_i32 v3, s26, v5
	.loc	1 79 37                         ; candidate.py:79:37
	ml_cmp_gt_i32 tcr, s21, v3
	.loc	1 78 36                         ; candidate.py:78:36
	sl_mull_u32 s8, s8, s25
	.loc	1 79 31                         ; candidate.py:79:31
	sl_and_b64 {s[0:1], wcr}, tcr, s[0:1]
	sl_and_b64 {s[2:3], wcr}, tcr, s[2:3]
	sl_and_b64 {s[4:5], wcr}, tcr, s[14:15]
	sl_and_b64 {s[6:7], wcr}, s[12:13], tcr
	.loc	1 78 36                         ; candidate.py:78:36
	sl_mull_u32 s12, s27, s25
	.loc	1 78 48 is_stmt 0               ; candidate.py:78:48
	ml_add_i32 v5, s12, v3
	.loc	1 78 36                         ; candidate.py:78:36
	sl_mull_u32 s12, s24, s25
	.loc	1 78 48                         ; candidate.py:78:48
	ml_add_i32 v7, s12, v3
	.loc	1 78 36                         ; candidate.py:78:36
	sl_mull_u32 s12, s23, s25
	.loc	1 78 48                         ; candidate.py:78:48
	ml_add_i32 v8, s12, v3
	ml_add_i32 v3, s8, v3
	.loc	1 78 22                         ; candidate.py:78:22
	ml_sra_b32 v9, v3, 0x1f
	ml_shl_b32 v10, v3, 0x2
	ml_shl_b32 v9, v9, 0x2
	ml_addo_u32 {v10, tcr}, s18, v10
	ml_srl_b32 v11, v3, 0x1e
	ml_or_b32 v9, v9, v11
	ml_mov_b32 v11, s19
	ml_addc_i32 v9, v11, v9, tcr
	.loc	1 82 54 is_stmt 1               ; candidate.py:82:54
	sl_barrier 
	ml_shl_b32 v4, v4, 0x2
	ml_shl_b32 v11, tid, 0x6
	ml_and_b32 v11, v11, 0x400
	ml_and_b32 v12, tid, 0x20
	ml_cmp_eq_u32 tcr, v12, 0x0
	ml_mov_b32 v13, 0x240
	ml_csel_b32 v13, 0, v13, tcr
	sl_and_b32 {s8, wcr}, s44, 0x40
	sl_mull_u32 s12, s8, 0x20
	sl_srl_b32 {s13, wcr}, s44, 0x1
	sl_and_b32 {s14, wcr}, s13, 0x40
	sl_and_b32 {s15, wcr}, s44, 0x100
	ml_anyop3_b32 v13, v13, v4, 60, 0xffffffea
	sl_mov_b32 s18, 0x1000504
	ml_byte_permute_b32 v2, v2, v6, s18
	sl_add_i32 s12, s15, s12
	ml_anyop3_b32 v6, s14, v13, v11, 0xfffffff6
	ml_slb_store_b32x1  v2, v6, s12, #0, null
	ml_byte_permute_b32 v0, v1, v0, s18
	ml_slb_store_b32x1  v0, v6, s12, #128, null
	sl_wait lmcnt(0)
	sl_barrier 
	sl_and_b32 {s12, wcr}, s13, 0xc0
	ml_shl_b32 v0, v12, 0x1
	sl_mull_u32 s8, s8, 0x10
	sl_mov_b32 s13, 0x23c
	ml_mov_b32 v1, s12
	ml_anyop3_b32 v1, s13, v4, v1, 0xfffffff8
	.loc	1 82 40 is_stmt 0               ; candidate.py:82:40
	ml_anyop3_b32 v0, v1, v0, v11, 0xfffffff6
	ml_add_i32 v0, v11, v0
	ml_slb_load_b32x1  v1, v0, s8, #0, null
	.loc	1 82 54                         ; candidate.py:82:54
	ml_mov_b32 v2, s22
	ml_mov_b32 v4, s9
	ml_rcp_f32 v2, v2
	.loc	1 82 40                         ; candidate.py:82:40
	ml_slb_load_b32x1  v0, v0, s8, #256, null
	.loc	1 82 54                         ; candidate.py:82:54
	sl_xor_b32 {s8, wcr}, s22, 0x80000000
	ml_mov_b32 v13, s17
	ml_rcp_f32 v4, v4
	.loc	1 83 20 is_stmt 1               ; candidate.py:83:20
	ml_mov_v2s_b32 s12, v10, 0x0
	ml_mov_v2s_b32 s13, v9, 0x0
	sl_mov_b32 s15, 0xffffffff
	.loc	1 82 54                         ; candidate.py:82:54
	ml_rcp_f32 v13, v13
	.loc	1 83 20                         ; candidate.py:83:20
	ml_mov_b32 v9, s12
	ml_sub_i32 v9, v10, v9
	.loc	1 82 40                         ; candidate.py:82:40
	sl_wait lmcnt(1)
	ml_shl_b32 v6, v1, 0x10
	ml_and_b32 v1, v1, 0xffff0000
	.loc	1 82 54 is_stmt 0               ; candidate.py:82:54
	ml_mul_f32 v12, v6, v2
	ml_fma_f32 v6, s8, v12, v6
	.loc	1 82 40                         ; candidate.py:82:40
	sl_wait lmcnt(0)
	ml_shl_b32 v11, v0, 0x10
	ml_and_b32 v0, v0, 0xffff0000
	.loc	1 82 54                         ; candidate.py:82:54
	ml_fma_f32 v2, v2, v6, v12
	ml_mov_b32 v6, 0x99
	ml_cmp_class_f32 tcr, v12, v6
	ml_csel_b32 v2, v12, v2, tcr
	ml_mul_f32 v12, v1, v4
	sl_xor_b32 {s8, wcr}, s9, 0x80000000
	ml_fma_f32 v1, s8, v12, v1
	ml_fma_f32 v1, v4, v1, v12
	ml_cmp_class_f32 tcr, v12, v6
	ml_csel_b32 v1, v12, v1, tcr
	ml_mul_f32 v4, v11, v13
	ml_mov_b32 v12, s16
	sl_xor_b32 {s8, wcr}, s17, 0x80000000
	ml_rcp_f32 v12, v12
	ml_fma_f32 v11, s8, v4, v11
	ml_fma_f32 v11, v13, v11, v4
	ml_cmp_class_f32 tcr, v4, v6
	ml_csel_b32 v4, v4, v11, tcr
	sl_xor_b32 {s8, wcr}, s16, 0x80000000
	ml_mul_f32 v11, v0, v12
	ml_fma_f32 v0, s8, v11, v0
	.loc	1 83 20 is_stmt 1               ; candidate.py:83:20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[6:7], tmsk
	ml_lsa_store_dword v2, s[12:15], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	ml_sub_i32 v2, v8, v3
	ml_shl_b32 v2, v2, 0x2
	ml_mov_v2s_b32 s6, v2, 0x0
	ml_sub_i32 v2, v7, v3
	ml_shl_b32 v2, v2, 0x2
	ml_mov_v2s_b32 s7, v2, 0x0
	.loc	1 82 54                         ; candidate.py:82:54
	ml_fma_f32 v0, v12, v0, v11
	.loc	1 83 20                         ; candidate.py:83:20
	ml_add_i32 v2, s6, v9
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[4:5], tmsk
	ml_lsa_store_dword v1, s[12:15], signed v2, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	ml_add_i32 v1, s7, v9
	ml_sub_i32 v2, v5, v3
	ml_shl_b32 v2, v2, 0x2
	ml_mov_v2s_b32 s4, v2, 0x0
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[2:3], tmsk
	ml_lsa_store_dword v4, s[12:15], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 82 54                         ; candidate.py:82:54
	ml_cmp_class_f32 tcr, v11, v6
	ml_csel_b32 v0, v11, v0, tcr
	.loc	1 83 20                         ; candidate.py:83:20
	ml_add_i32 v1, s4, v9
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v0, s[12:15], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 80 4                          ; candidate.py:80:4
	sl_eop 
.Ltmp20:
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	head_temperature_kernel.kd
	.type	head_temperature_kernel.kd,@object
	.size	head_temperature_kernel.kd, 64
head_temperature_kernel.kd:
	.asciz	"\000\000\000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	head_temperature_kernel@rel64-head_temperature_kernel.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	536965
	.asciz	"\003\000\264\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	head_temperature_kernel, .Lfunc_end0-head_temperature_kernel
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 3856
; NumSgprs: 49
; NumVgprs: 21
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 6
; VGPRBlocks: 5
; NumSGPRsForWarpsPerNU: 45
; NumVGPRsForWarpsPerNR: 21
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
	.long	252                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0xf5 DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"candidate.py"                  ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/workspace/experiments/minicpm-s2/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/source" ; DW_AT_comp_dir
	.byte	0
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.byte	2                               ; Abbrev [2] 0xab:0x1a DW_TAG_subprogram
	.ascii	"head_temperature_kernel"       ; DW_AT_name
	.byte	0
	.byte	1                               ; DW_AT_inline
	.byte	3                               ; Abbrev [3] 0xc5:0x3a DW_TAG_subprogram
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.long	171                             ; DW_AT_abstract_origin
	.byte	4                               ; Abbrev [4] 0xda:0xc DW_TAG_inlined_subroutine
	.long	171                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges0                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	33                              ; DW_AT_call_line
	.byte	24                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0xe6:0xc DW_TAG_inlined_subroutine
	.long	171                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges1                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	32                              ; DW_AT_call_line
	.byte	24                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0xf2:0xc DW_TAG_inlined_subroutine
	.long	171                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges2                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	51                              ; DW_AT_call_line
	.byte	37                              ; DW_AT_call_column
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
	.quad	.Ltmp16-.Lfunc_begin0
	.quad	.Ltmp17-.Lfunc_begin0
	.quad	.Ltmp18-.Lfunc_begin0
	.quad	.Ltmp19-.Lfunc_begin0
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
      - .name:           KArg_4
        .offset:         32
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_5
        .offset:         36
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_6
        .offset:         40
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_7
        .offset:         44
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_8
        .offset:         48
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_9
        .offset:         52
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_10
        .offset:         56
        .size:           4
        .value_kind:     by_value
      - .address_space:  global
        .name:           KArg_11
        .offset:         64
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_12
        .offset:         72
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_13
        .offset:         80
        .size:           8
        .value_kind:     global_buffer
    .group_segment_fixed_size: 0
    .kernarg_segment_align: 8
    .kernarg_segment_size: 88
    .max_flat_workgroup_size: 0
    .name:           head_temperature_kernel
    .private_segment_fixed_size: 0
    .sgpr_count:     49
    .sgpr_spill_count: 0
    .symbol:         head_temperature_kernel.kd
    .vgpr_count:     21
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
