	.text
	.globl	linear_kernel                   ; -- Begin function linear_kernel
	.p2align	3
	.type	linear_kernel,@function
	.iluvatar_kernel linear_kernel
linear_kernel:                          ; @linear_kernel
.Lfunc_begin0:
	.file	1 "/usr/local/lib/python3.12/site-packages/flag_gems/runtime/backend/_iluvatar/ops" "linear.py"
	.loc	1 38 0                          ; linear.py:38:0
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
		granulated_workitem_vgpr_count = 7
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
		kernarg_segment_byte_size = 80
		workgroup_fbarrier_count = 0
		warp_sgpr_count = 39
		workitem_vgpr_count = 31
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
	sl_mov_b32 s28, tcr_lo
	ml_vrf_init_u32 v16, tcr
.Ltmp0:
	.file	2 "/usr/local/lib/python3.12/site-packages/triton/language" "standard.py"
	.loc	2 65 17 prologue_end            ; standard.py:65:17 @[ linear.py:64:24 ]
	sl_lsa_load_b32x16 s[12:27], s[4:5], noreg, #0, ca
.Ltmp1:
	.loc	2 65 17 is_stmt 0               ; standard.py:65:17 @[ linear.py:63:24 ]
	sl_wait smcnt(0)
	sl_add_i32 s0, s20, 0x3f
.Ltmp2:
	.loc	2 65 17                         ; standard.py:65:17 @[ linear.py:64:24 ]
	sl_add_i32 s1, s21, 0xff
.Ltmp3:
	.loc	2 65 30                         ; standard.py:65:30 @[ linear.py:63:24 ]
	sl_sra_b32 {s2, wcr}, s0, 0x1f
.Ltmp4:
	.loc	2 65 30                         ; standard.py:65:30 @[ linear.py:64:24 ]
	sl_sra_b32 {s3, wcr}, s1, 0x1f
.Ltmp5:
	.loc	2 65 30                         ; standard.py:65:30 @[ linear.py:63:24 ]
	sl_srl_b32 {s2, wcr}, s2, 0x1a
.Ltmp6:
	.loc	2 65 30                         ; standard.py:65:30 @[ linear.py:64:24 ]
	sl_srl_b32 {s3, wcr}, s3, 0x18
.Ltmp7:
	.loc	2 65 30                         ; standard.py:65:30 @[ linear.py:63:24 ]
	sl_add_i32 s0, s0, s2
.Ltmp8:
	.loc	2 65 30                         ; standard.py:65:30 @[ linear.py:64:24 ]
	sl_add_i32 s1, s1, s3
.Ltmp9:
	.loc	2 65 30                         ; standard.py:65:30 @[ linear.py:63:24 ]
	sl_sra_b32 {s5, wcr}, s0, 0x6
.Ltmp10:
	.loc	2 65 30                         ; standard.py:65:30 @[ linear.py:64:24 ]
	sl_sra_b32 {s0, wcr}, s1, 0x8
.Ltmp11:
	.loc	1 66 22 is_stmt 1               ; linear.py:66:22
	sl_shl_b32 {s4, wcr}, s0, 0x3
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_abs_i32 s8, s4
	ml_cvt_f32_u32  v0, s8
	sl_reg_read s2, hwreg(HW_REG_MODE)
	ml_rcp_f32 v0, v0
	sl_sra_b32 {s26, wcr}, s1, 0x1f
	sl_or_b32 {s1, wcr}, s2, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s2
	ml_mov_v2s_b32 s1, v0, 0x0
	sl_mul_u64_u32 s[2:3], s1, s8
	sl_neg_i32 s9, s2
	sl_cmp_eq_u32 wcr, s3, 0x0
	sl_csel_b32 s2, s9, s2, wcr
	sl_mul_u64_u32 s[2:3], s2, s1
	sl_add_i32 s2, s1, s3
	sl_sub_i32 s1, s1, s3
	sl_csel_b32 s1, s2, s1, wcr
	sl_mul_u64_u32 s[2:3], s1, s6
	sl_mull_u32 s1, s3, s8
	sl_sub_i32 s2, s6, s1
	sl_cmp_ge_u32 wcr, s2, s8
	sl_sub_bi_u64 s[8:9], s[10:11], s[10:11], wcr
	sl_cmp_ge_u32 wcr, s6, s1
	sl_sub_bi_u32 s1, s10, s10, wcr
	sl_sub_bi_u64 s[16:17], s[10:11], s[10:11], wcr
	sl_and_b64 {s[8:9], wcr}, s[8:9], s[16:17]
	sl_mov_b32 s2, 0xffffffff
	sl_or_b32 {s8, wcr}, s8, s9
	sl_csel_b32 s8, s2, 0x0, wcr
	sl_cmp_eq_u32 wcr, s8, 0x0
	sl_add_i32 s8, s3, 0x1
	sl_add_i32 s9, s3, 0xffffffff
	sl_csel_b32 s3, s3, s8, wcr
	sl_or_b32 {s1, wcr}, s1, 0x0
	sl_csel_b32 s1, s3, s9, wcr
	sl_xor_b32 {s1, wcr}, s1, s26
	sl_sub_i32 s1, s1, s26
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s29, s1, 0xffffffff, wcr
	.loc	1 67 41                         ; linear.py:67:41
	sl_mull_u32 s3, s29, 0x8
	.loc	1 67 30 is_stmt 0               ; linear.py:67:30
	sl_sub_i32 s0, s5, s3
	.loc	1 67 50                         ; linear.py:67:50
	sl_min_i32 s5, s0, 0x8
	.loc	1 68 40 is_stmt 1               ; linear.py:68:40
	sl_abs_i32 s27, s5
	ml_cvt_f32_u32  v0, s27
	sl_reg_read s0, hwreg(HW_REG_MODE)
	ml_rcp_f32 v0, v0
	sl_sra_b32 {s30, wcr}, s5, 0x1f
	sl_or_b32 {s1, wcr}, s0, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s0
	ml_mov_v2s_b32 s8, v0, 0x0
	sl_mul_u64_u32 s[0:1], s8, s27
	sl_neg_i32 s9, s0
	sl_cmp_eq_u32 wcr, s1, 0x0
	sl_csel_b32 s0, s9, s0, wcr
	sl_mul_u64_u32 s[0:1], s0, s8
	sl_add_i32 s0, s8, s1
	sl_sub_i32 s1, s8, s1
	sl_csel_b32 s31, s0, s1, wcr
	sl_mul_u64_u32 s[0:1], s31, s6
	sl_mull_u32 s0, s1, s27
	sl_sub_i32 s1, s6, s0
	sl_cmp_ge_u32 wcr, s1, s27
	sl_sub_bi_u64 s[8:9], s[10:11], s[10:11], wcr
	sl_cmp_ge_u32 wcr, s6, s0
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_sub_bi_u64 s[16:17], s[10:11], s[10:11], wcr
	sl_and_b64 {s[8:9], wcr}, s[8:9], s[16:17]
	sl_or_b32 {s8, wcr}, s8, s9
	sl_csel_b32 s8, s2, 0x0, wcr
	sl_cmp_eq_u32 wcr, s8, 0x0
	sl_sub_i32 s8, s1, s27
	sl_add_i32 s9, s1, s27
	sl_csel_b32 s1, s1, s8, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s1, s9, wcr
	sl_cmp_ne_u32 wcr, s5, 0x0
	sl_csel_b32 s0, s0, 0xffffffff, wcr
	.loc	1 68 34 is_stmt 0               ; linear.py:68:34
	sl_add_i32 s0, s3, s0
	.loc	1 73 48 is_stmt 1               ; linear.py:73:48
	sl_abs_i32 s3, s20
	ml_cvt_f32_u32  v0, s3
	.loc	1 71 17                         ; linear.py:71:17
	sl_mull_u32 s16, s0, 0x40
	.loc	1 73 48                         ; linear.py:73:48
	ml_rcp_f32 v0, v0
	.loc	1 71 40                         ; linear.py:71:40
	sl_bfe2_b32 s17, tcr_lo, 0x86
	.loc	1 73 48                         ; linear.py:73:48
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_sra_b32 {s26, wcr}, s16, 0x1f
	sl_abs_i32 s32, s16
	sl_or_b32 {s1, wcr}, s0, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s0
	ml_mov_v2s_b32 s8, v0, 0x0
	.loc	1 75 17                         ; linear.py:75:17
	sl_mull_u32 s7, s7, 0x20
	.loc	1 73 48                         ; linear.py:73:48
	sl_mul_u64_u32 s[0:1], s8, s3
	sl_neg_i32 s9, s0
	sl_cmp_eq_u32 wcr, s1, 0x0
	sl_csel_b32 s0, s9, s0, wcr
	sl_mul_u64_u32 s[0:1], s0, s8
	sl_add_i32 s0, s8, s1
	sl_sub_i32 s1, s8, s1
	sl_csel_b32 s0, s0, s1, wcr
	sl_mul_u64_u32 s[0:1], s0, s32
	sl_mull_u32 s0, s1, s3
	sl_sub_i32 s1, s32, s0
	sl_cmp_ge_u32 wcr, s1, s3
	sl_sub_bi_u64 s[8:9], s[10:11], s[10:11], wcr
	sl_cmp_ge_u32 wcr, s32, s0
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_sub_bi_u64 s[32:33], s[10:11], s[10:11], wcr
	sl_and_b64 {s[8:9], wcr}, s[8:9], s[32:33]
	sl_or_b32 {s8, wcr}, s8, s9
	sl_csel_b32 s8, s2, 0x0, wcr
	sl_cmp_eq_u32 wcr, s8, 0x0
	sl_sub_i32 s8, s1, s3
	sl_add_i32 s3, s1, s3
	sl_csel_b32 s1, s1, s8, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s1, s3, wcr
	sl_xor_b32 {s0, wcr}, s0, s26
	sl_sub_i32 s0, s0, s26
	sl_cmp_ne_u32 wcr, s20, 0x0
	sl_csel_b32 s0, s0, 0xffffffff, wcr
	.loc	1 77 36                         ; linear.py:77:36
	sl_mull_u32 s0, s0, s23
	.loc	1 77 48 is_stmt 0               ; linear.py:77:48
	sl_add_i32 s8, s0, s7
	.loc	1 77 21                         ; linear.py:77:21
	sl_sra_b32 {s9, wcr}, s8, 0x1f
	.loc	1 83 24 is_stmt 1               ; linear.py:83:24
	sl_cmp_lt_u32 wcr, s17, 0x4
	sl_mull_u32 s3, s23, 0x2
	sl_mull_u32 s26, s17, 0x400
	sl_cbr_wcrz BB0_2, wcr
; %bb.1:
	.loc	1 77 21                         ; linear.py:77:21
	sl_shl_b64 {s[0:1], wcr}, s[8:9], 0x1
	sl_add_i64 s[0:1], s[12:13], s[0:1]
	.loc	1 83 24                         ; linear.py:83:24
	sl_add_i32 s33, s26, 0x8000
	sl_mull_u32 s34, s17, 0x20
	sl_mull_u32 s32, s23, s34
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[32:33], 0x0, 0x0, 0x0, 0x1
	sl_jump BB0_3
BB0_2:                                  ; %._crit_edge57
	.loc	1 84 24                         ; linear.py:84:24
	sl_mull_u32 s34, s17, 0x20
BB0_3:
	.loc	1 69 19                         ; linear.py:69:19
	sl_mull_u32 s0, s29, s4
	sl_sub_i32 s0, s6, s0
	.loc	1 69 29 is_stmt 0               ; linear.py:69:29
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_xor_b32 {s2, wcr}, s1, s30
	sl_abs_i32 s4, s0
	sl_mul_u64_u32 s[0:1], s31, s4
	sl_mull_u32 s0, s1, s27
	sl_sub_i32 s6, s4, s0
	sl_cmp_ge_u32 wcr, s6, s27
	sl_sub_bi_u64 s[30:31], s[10:11], s[10:11], wcr
	sl_cmp_ge_u32 wcr, s4, s0
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_sub_bi_u64 s[32:33], s[10:11], s[10:11], wcr
	sl_and_b64 {s[32:33], wcr}, s[30:31], s[32:33]
	sl_mov_b32 s30, 0xffffffff
	sl_or_b32 {s32, wcr}, s32, s33
	sl_csel_b32 s4, s30, 0x0, wcr
	sl_cmp_eq_u32 wcr, s4, 0x0
	sl_add_i32 s4, s1, 0x1
	sl_add_i32 s6, s1, 0xffffffff
	sl_csel_b32 s1, s1, s4, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s1, s6, wcr
	sl_xor_b32 {s0, wcr}, s0, s2
	sl_sub_i32 s0, s0, s2
	sl_cmp_ne_u32 wcr, s5, 0x0
	sl_csel_b32 s0, s0, 0xffffffff, wcr
	.loc	1 71 40 is_stmt 1               ; linear.py:71:40
	sl_and_b32 {s27, wcr}, s28, 0x200
	.loc	1 74 48                         ; linear.py:74:48
	sl_abs_i32 s2, s21
	ml_cvt_f32_u32  v0, s2
	.loc	1 72 17                         ; linear.py:72:17
	sl_mull_u32 s32, s0, 0x100
	.loc	1 74 48                         ; linear.py:74:48
	ml_rcp_f32 v0, v0
	.loc	1 72 40                         ; linear.py:72:40
	sl_and_b32 {s33, wcr}, s28, 0x1c0
	.loc	1 74 48                         ; linear.py:74:48
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_sra_b32 {s6, wcr}, s32, 0x1f
	sl_abs_i32 s28, s32
	sl_or_b32 {s1, wcr}, s0, 0x3
	ml_mul_f32 v0, v0, 0x4f800000
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_u32_f32  v0, v0
	sl_reg_write hwreg(HW_REG_MODE), s0
	ml_mov_v2s_b32 s4, v0, 0x0
	.loc	1 84 24                         ; linear.py:84:24
	sl_mull_u32 s31, s24, 0x2
	ml_mov_b32 v19, 0x0
	ml_mov_b32 v20, 0x0
	.loc	1 74 48                         ; linear.py:74:48
	sl_mul_u64_u32 s[0:1], s4, s2
	sl_neg_i32 s5, s0
	sl_cmp_eq_u32 wcr, s1, 0x0
	sl_csel_b32 s0, s5, s0, wcr
	sl_mul_u64_u32 s[0:1], s0, s4
	sl_add_i32 s0, s4, s1
	sl_sub_i32 s1, s4, s1
	sl_csel_b32 s0, s0, s1, wcr
	sl_mul_u64_u32 s[0:1], s0, s28
	sl_mull_u32 s0, s1, s2
	sl_sub_i32 s1, s28, s0
	sl_cmp_ge_u32 wcr, s1, s2
	sl_sub_bi_u64 s[4:5], s[10:11], s[10:11], wcr
	sl_cmp_ge_u32 wcr, s28, s0
	sl_sub_bi_u32 s0, s10, s10, wcr
	sl_sub_bi_u64 s[28:29], s[10:11], s[10:11], wcr
	sl_and_b64 {s[4:5], wcr}, s[4:5], s[28:29]
	sl_or_b32 {s4, wcr}, s4, s5
	sl_csel_b32 s4, s30, 0x0, wcr
	sl_cmp_eq_u32 wcr, s4, 0x0
	sl_sub_i32 s4, s1, s2
	sl_add_i32 s2, s1, s2
	sl_csel_b32 s1, s1, s4, wcr
	sl_or_b32 {s0, wcr}, s0, 0x0
	sl_csel_b32 s0, s1, s2, wcr
	sl_xor_b32 {s0, wcr}, s0, s6
	sl_sub_i32 s0, s0, s6
	sl_cmp_ne_u32 wcr, s21, 0x0
	sl_csel_b32 s0, s0, 0xffffffff, wcr
	.loc	1 78 63                         ; linear.py:78:63
	sl_mull_u32 s0, s0, s24
	.loc	1 78 48 is_stmt 0               ; linear.py:78:48
	sl_add_i32 s0, s0, s7
	.loc	1 78 22                         ; linear.py:78:22
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x1
	sl_add_i64 s[28:29], s[14:15], s[0:1]
	.loc	1 84 24 is_stmt 1               ; linear.py:84:24
	sl_mull_u32 s4, s34, s24
	sl_mov_b32 s5, s26
	sl_sme_load_16x1b64_col s[28:31], s[4:5], 0x0, 0x0, 0x0, 0x1
.Ltmp12:
	.loc	2 65 17                         ; standard.py:65:17 @[ linear.py:82:37 ]
	sl_add_i32 s0, s22, 0x1f
.Ltmp13:
	.loc	1 82 26                         ; linear.py:82:26
	sl_cmp_gt_i32 wcr, s0, 0x1f
	sl_mov_b32 s14, 0x0
	ml_mov_b32 v21, 0x0
	ml_mov_b32 v22, 0x0
	ml_mov_b32 v17, 0x0
	ml_mov_b32 v18, 0x0
	ml_mov_b32 v8, 0x0
	ml_mov_b32 v9, 0x0
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v2, 0x0
	ml_mov_b32 v4, 0x0
	ml_mov_b32 v6, 0x0
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v3, 0x0
	ml_mov_b32 v5, 0x0
	ml_mov_b32 v7, 0x0
	sl_cbr_wcrz BB0_9, wcr
; %bb.4:                                ; %.lr.ph
.Ltmp14:
	.loc	2 65 30                         ; standard.py:65:30 @[ linear.py:82:37 ]
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_srl_b32 {s1, wcr}, s1, 0x1b
	sl_add_i32 s0, s0, s1
	sl_sra_b32 {s15, wcr}, s0, 0x5
	ml_shl_b32 v0, v16, 0x2
	ml_and_b32 v0, v0, 0xfc
	sl_mull_u32 s0, s27, 0x2
	ml_add_i32 v17, s0, v0
	ml_shl_b32 v1, v16, 0x6
	ml_and_b32 v1, v1, 0x300
	sl_mull_u32 s0, s33, 0x10
	ml_anyop3_b32 v18, s0, v1, v0, 0xfffffffe
	ml_xor_b32 v19, v18, 0x10
	ml_xor_b32 v20, v18, 0x20
	ml_xor_b32 v21, v18, 0x30
	sl_mull_u32 s0, s17, s23
	sl_mull_u32 s6, s0, 0x20
.Ltmp15:
	.loc	1 82 26                         ; linear.py:82:26
	sl_add_i64 s[28:29], s[28:29], 0x40
	sl_shl_b64 {s[0:1], wcr}, s[8:9], 0x1
	sl_add_i64 s[0:1], s[12:13], s[0:1]
	sl_add_i64 s[0:1], s[0:1], 0x40
	ml_mov_b32 v0, 0x0
	ml_xor_b32 v22, v17, 0x80
	sl_mov_b32 s8, s30
	ml_mov_b32 v1, 0x0
	ml_mov_b32 v10, 0x0
	ml_mov_b32 v11, 0x0
	ml_mov_b32 v12, 0x0
	ml_mov_b32 v13, 0x0
	ml_mov_b32 v14, 0x0
	ml_mov_b32 v15, 0x0
	sl_jump BB0_6
BB0_5:                                  ;   in Loop: Header=BB0_6 Depth=1
	.loc	1 84 24                         ; linear.py:84:24
	sl_mull_u32 s2, s14, 0x4000
	sl_add_i32 s5, s26, s2
	sl_sme_load_16x1b64_col s[28:31], s[4:5], 0x0, 0x0, 0x0, 0x1
	.loc	1 82 26                         ; linear.py:82:26
	sl_add_i64 s[28:29], s[28:29], 0x40
	sl_add_i32 s15, s15, 0xffffffff
	sl_cmp_eq_u32 wcr, s15, 0x0
	sl_add_i64 s[0:1], s[0:1], 0x40
	sl_cbr_wcrnz BB0_8, wcr
BB0_6:                                  ; =>This Inner Loop Header: Depth=1
	sl_add_i32 s2, s8, 0x1
	sl_cmp_lt_i32 wcr, s2, 0x2
	sl_csel_b32 s8, s2, 0x0, wcr
	.loc	1 83 24                         ; linear.py:83:24
	sl_wait g2scnt(0)
	sl_barrier_req 0x0
	sl_barrier_wait 0x0
	sl_mull_u32 s2, s8, 0x1000
	sl_add_i32 s5, s2, 0x8000
	ml_slb_load_b32x1  v23, v17, s5, #0, null
	.loc	1 84 24                         ; linear.py:84:24
	sl_mull_u32 s7, s8, 0x4000
	sl_add_i32 s9, s7, 0x2000
	.loc	1 83 24                         ; linear.py:83:24
	sl_add_i32 s2, s2, 0x8800
	ml_slb_load_b32x1  v24, v17, s5, #256, null
	.loc	1 82 26                         ; linear.py:82:26
	sl_add_i32 s12, s14, 0x1
	sl_cmp_lt_i32 wcr, s12, 0x2
	sl_csel_b32 s14, s12, 0x0, wcr
	.loc	1 84 24                         ; linear.py:84:24
	ml_slb_load_b32x1  v25, v18, s7, #0, null
	.loc	1 83 24                         ; linear.py:83:24
	sl_cmp_lt_u32 wcr, s17, 0x4
	.loc	1 84 24                         ; linear.py:84:24
	ml_slb_load_b32x1  v26, v19, s7, #0, null
	ml_slb_load_b32x1  v27, v18, s9, #0, null
	ml_slb_load_b32x1  v28, v19, s9, #0, null
	.loc	1 83 24                         ; linear.py:83:24
	ml_slb_load_b32x1  v29, v17, s2, #0, null
	ml_slb_load_b32x1  v30, v17, s2, #256, null
	.loc	1 85 29                         ; linear.py:85:29
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[23:24], v[25:26], v[0:3]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[23:24], v[27:28], v[4:7]
	.loc	1 83 24                         ; linear.py:83:24
	ml_slb_load_b32x1  v23, v22, s5, #512, null
	ml_slb_load_b32x1  v24, v22, s5, #768, null
	.loc	1 85 29                         ; linear.py:85:29
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[29:30], v[25:26], v[8:11]
	.loc	1 84 24                         ; linear.py:84:24
	ml_slb_load_b32x1  v25, v20, s7, #0, null
	ml_slb_load_b32x1  v26, v21, s7, #0, null
	.loc	1 85 29                         ; linear.py:85:29
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[29:30], v[27:28], v[12:15]
	.loc	1 84 24                         ; linear.py:84:24
	ml_slb_load_b32x1  v27, v20, s9, #0, null
	ml_slb_load_b32x1  v28, v21, s9, #0, null
	.loc	1 83 24                         ; linear.py:83:24
	ml_slb_load_b32x1  v29, v22, s2, #512, null
	ml_slb_load_b32x1  v30, v22, s2, #768, null
	.loc	1 85 29                         ; linear.py:85:29
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[23:24], v[25:26], v[0:3]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[23:24], v[27:28], v[4:7]
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[29:30], v[25:26], v[8:11]
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[29:30], v[27:28], v[12:15]
	.loc	1 83 24                         ; linear.py:83:24
	sl_cbr_wcrz BB0_5, wcr
; %bb.7:                                ;   in Loop: Header=BB0_6 Depth=1
	.loc	1 0 24 is_stmt 0                ; linear.py:0:24
	sl_mull_u32 s2, s14, 0x1000
	sl_add_i32 s2, s26, s2
	sl_add_i32 s7, s2, 0x8000
	sl_mov_b32 s2, s30
	.loc	1 83 24                         ; linear.py:83:24
	sl_sme_load_16x1b64_rowxfb16 s[0:3], s[6:7], 0x0, 0x0, 0x0, 0x1
	sl_jump BB0_5
BB0_8:                                  ; %._crit_edge.loopexit
	.loc	1 112 27 is_stmt 1              ; linear.py:112:27
	ml_cvt_bf16_f32  v19, v0
	ml_cvt_bf16_f32  v20, v1
	ml_cvt_bf16_f32  v21, v2
	ml_cvt_bf16_f32  v22, v3
	ml_cvt_bf16_f32  v17, v8
	ml_cvt_bf16_f32  v18, v9
	ml_cvt_bf16_f32  v8, v10
	ml_cvt_bf16_f32  v9, v11
	ml_cvt_bf16_f32  v0, v4
	ml_cvt_bf16_f32  v2, v5
	ml_cvt_bf16_f32  v4, v6
	ml_cvt_bf16_f32  v6, v7
	ml_cvt_bf16_f32  v1, v12
	ml_cvt_bf16_f32  v3, v13
	ml_cvt_bf16_f32  v5, v14
	ml_cvt_bf16_f32  v7, v15
BB0_9:                                  ; %._crit_edge
	.loc	1 72 40                         ; linear.py:72:40
	ml_shl_b32 v15, v16, 0x1
	ml_and_b32 v10, v15, 0xe
	sl_srl_b32 {s0, wcr}, s33, 0x2
	.loc	1 72 27 is_stmt 0               ; linear.py:72:27
	sl_add_i32 s0, s32, s0
	ml_add_i32 v23, s0, v10
	ml_add_i32 v24, v23, 0x80
	.loc	1 71 40 is_stmt 1               ; linear.py:71:40
	sl_srl_b32 {s0, wcr}, s27, 0x5
	ml_bfe2_b32 v10, v16, 0x63
	.loc	1 71 27 is_stmt 0               ; linear.py:71:27
	sl_add_i32 s0, s16, s0
	ml_add_i32 v14, s0, v10
	ml_add_i32 v16, v14, 0x28
	ml_add_i32 v25, v14, 0x20
	ml_add_i32 v26, v14, 0x8
	.loc	1 82 26 is_stmt 1               ; linear.py:82:26
	sl_wait g2scnt(0)
	sl_barrier 
	.loc	1 109 36                        ; linear.py:109:36
	ml_mul_u64_u32 v[10:11], s25, v14
	.loc	1 112 27                        ; linear.py:112:27
	sl_mov_b32 s22, 0x2010200
	.loc	1 109 36                        ; linear.py:109:36
	ml_mul_u64_u32 v[11:12], s25, v26
	ml_mul_u64_u32 v[12:13], s25, v25
	.loc	1 109 48 is_stmt 0              ; linear.py:109:48
	ml_add_i32 v27, v23, v10
	.loc	1 109 22                        ; linear.py:109:22
	ml_sra_b32 v13, v27, 0x1f
	ml_shl_b32 v28, v27, 0x1
	ml_shl_b32 v13, v13, 0x1
	ml_addo_u32 {v28, tcr}, s18, v28
	ml_srl_b32 v29, v27, 0x1f
	ml_or_b32 v13, v13, v29
	ml_mov_b32 v29, s19
	ml_addc_i32 v29, v29, v13, tcr
	.loc	1 110 17 is_stmt 1              ; linear.py:110:17
	ml_cmp_gt_i32 tcr, s20, v14
	.loc	1 109 36                        ; linear.py:109:36
	ml_mul_u64_u32 v[13:14], s25, v16
	.loc	1 112 27                        ; linear.py:112:27
	sl_mov_b32 s18, 0x1000504
	.loc	1 112 20 is_stmt 0              ; linear.py:112:20
	sl_mov_b32 s19, s30
	.loc	1 110 17 is_stmt 1              ; linear.py:110:17
	sl_mov_b64 s[2:3], tcr
	ml_cmp_gt_i32 tcr, s20, v26
	.loc	1 112 27                        ; linear.py:112:27
	ml_byte_permute_b32 v14, v20, v19, s18
	ml_and_b32 v19, tid, 0x1
	ml_mov_b32 v20, 0x5410
	.loc	1 110 17                        ; linear.py:110:17
	sl_mov_b64 s[0:1], tcr
	ml_cmp_gt_i32 tcr, s20, v25
	.loc	1 112 27                        ; linear.py:112:27
	ml_byte_permute_b32 v17, v18, v17, s18
	ml_byte_permute_b32 v8, v9, v8, s18
	.loc	1 112 20 is_stmt 0              ; linear.py:112:20
	ml_mov_v2s_b32 s16, v28, 0x0
	.loc	1 110 17 is_stmt 1              ; linear.py:110:17
	sl_mov_b64 s[6:7], tcr
	ml_cmp_gt_i32 tcr, s20, v16
	.loc	1 112 27                        ; linear.py:112:27
	ml_byte_permute_b32 v16, v22, v21, s18
	ml_bfe2_b32 v22, tid, 0x25
	ml_anyop3_b32 v15, 62, v15, v22, 0xfffffff8
	.loc	1 110 17                        ; linear.py:110:17
	sl_mov_b64 s[4:5], tcr
	.loc	1 110 37 is_stmt 0              ; linear.py:110:37
	ml_cmp_gt_i32 tcr, s21, v23
	.loc	1 112 20 is_stmt 1              ; linear.py:112:20
	ml_mov_v2s_b32 s17, v29, 0x0
	.loc	1 110 37                        ; linear.py:110:37
	sl_mov_b64 s[12:13], tcr
	ml_cmp_gt_i32 tcr, s21, v24
	.loc	1 110 31 is_stmt 0              ; linear.py:110:31
	sl_and_b64 {s[14:15], wcr}, s[2:3], s[12:13]
	.loc	1 110 37                        ; linear.py:110:37
	sl_mov_b64 s[8:9], tcr
	.loc	1 112 27 is_stmt 1              ; linear.py:112:27
	ml_cmp_eq_u32 tcr, v19, 0x0
	ml_mov_b32 v19, 0x7632
	ml_csel_b32 v21, v20, v19, tcr
	ml_byte_permute_b32 v21, v21, v21, s22
	ml_pk_shl_b16 v21, v21, 0x40004
	ml_pk_srl_b8 v21, v21, 0x40004
	ml_byte_permute_b32 v22, v14, v16, v21
	ml_slb_shuffle_rtn_b32 v22, v22, v15
	ml_csel_b32 v18, v19, v20, tcr
	ml_byte_permute_b32 v18, v18, v18, s22
	ml_pk_shl_b16 v18, v18, 0x40004
	ml_pk_srl_b8 v18, v18, 0x40004
	ml_byte_permute_b32 v14, v14, v16, v18
	ml_xor_b32 v16, v15, 0x1
	ml_slb_shuffle_rtn_b32 v14, v14, v16
	ml_byte_permute_b32 v9, v17, v8, v21
	ml_byte_permute_b32 v8, v17, v8, v18
	ml_and_b32 v17, tid, 0x20
	ml_cmp_eq_u32 tcr, v17, 0x0
	ml_mov_b32 v17, 0x1054
	ml_csel_b32 v17, v20, v17, tcr
	ml_byte_permute_b32 v17, v17, v17, s22
	ml_pk_shl_b16 v17, v17, 0x40004
	ml_pk_srl_b8 v17, v17, 0x40004
	.loc	1 112 20 is_stmt 0              ; linear.py:112:20
	ml_mov_b32 v20, s16
	ml_sub_i32 v20, v28, v20
	.loc	1 112 27                        ; linear.py:112:27
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v25, v22, v14, v17
	.loc	1 112 20                        ; linear.py:112:20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[14:15], tmsk
	ml_lsa_store_dword v25, s[16:19], signed v20, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	ml_mov_b32 v25, 0x3276
	.loc	1 112 27                        ; linear.py:112:27
	ml_csel_b32 v19, v19, v25, tcr
	.loc	1 109 48 is_stmt 1              ; linear.py:109:48
	ml_add_i32 v25, v23, v11
	.loc	1 112 27                        ; linear.py:112:27
	ml_slb_shuffle_rtn_b32 v9, v9, v15
	.loc	1 112 20 is_stmt 0              ; linear.py:112:20
	ml_sub_i32 v25, v25, v27
	ml_shl_b32 v25, v25, 0x1
	ml_mov_v2s_b32 s20, v25, 0x0
	.loc	1 110 31 is_stmt 1              ; linear.py:110:31
	sl_and_b64 {s[14:15], wcr}, s[12:13], s[0:1]
	.loc	1 112 27                        ; linear.py:112:27
	ml_slb_shuffle_rtn_b32 v8, v8, v16
	ml_byte_permute_b32 v19, v19, v19, s22
	ml_pk_shl_b16 v19, v19, 0x40004
	ml_pk_srl_b8 v19, v19, 0x40004
	ml_byte_permute_b32 v14, v22, v14, v19
	.loc	1 112 20 is_stmt 0              ; linear.py:112:20
	ml_add_i32 v22, s20, v20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[14:15], tmsk
	ml_lsa_store_dword v14, s[16:19], signed v22, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 109 48 is_stmt 1              ; linear.py:109:48
	ml_add_i32 v14, v23, v12
	ml_add_i32 v22, v23, v13
	.loc	1 110 31                        ; linear.py:110:31
	sl_and_b64 {s[14:15], wcr}, s[12:13], s[6:7]
	.loc	1 112 20                        ; linear.py:112:20
	ml_sub_i32 v14, v14, v27
	ml_shl_b32 v14, v14, 0x1
	ml_mov_v2s_b32 s20, v14, 0x0
	.loc	1 112 27 is_stmt 0              ; linear.py:112:27
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v14, v9, v8, v17
	.loc	1 112 20                        ; linear.py:112:20
	ml_sub_i32 v22, v22, v27
	ml_shl_b32 v22, v22, 0x1
	ml_mov_v2s_b32 s21, v22, 0x0
	ml_add_i32 v22, s20, v20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[14:15], tmsk
	ml_lsa_store_dword v14, s[16:19], signed v22, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 110 31 is_stmt 1              ; linear.py:110:31
	sl_and_b64 {s[12:13], wcr}, s[12:13], s[4:5]
	.loc	1 112 27                        ; linear.py:112:27
	ml_byte_permute_b32 v8, v9, v8, v19
	.loc	1 112 20 is_stmt 0              ; linear.py:112:20
	ml_add_i32 v9, s21, v20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[12:13], tmsk
	ml_lsa_store_dword v8, s[16:19], signed v9, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 112 27                        ; linear.py:112:27
	ml_byte_permute_b32 v0, v2, v0, s18
	ml_byte_permute_b32 v2, v6, v4, s18
	ml_byte_permute_b32 v4, v0, v2, v21
	ml_slb_shuffle_rtn_b32 v4, v4, v15
	.loc	1 109 48 is_stmt 1              ; linear.py:109:48
	ml_add_i32 v6, v24, v10
	ml_add_i32 v8, v24, v11
	.loc	1 112 27                        ; linear.py:112:27
	ml_byte_permute_b32 v0, v0, v2, v18
	ml_slb_shuffle_rtn_b32 v0, v0, v16
	ml_byte_permute_b32 v1, v3, v1, s18
	ml_byte_permute_b32 v2, v7, v5, s18
	ml_byte_permute_b32 v3, v1, v2, v21
	ml_slb_shuffle_rtn_b32 v3, v3, v15
	.loc	1 109 48                        ; linear.py:109:48
	ml_add_i32 v5, v24, v12
	ml_add_i32 v7, v24, v13
	.loc	1 112 27                        ; linear.py:112:27
	ml_byte_permute_b32 v1, v1, v2, v18
	ml_slb_shuffle_rtn_b32 v1, v1, v16
	.loc	1 110 31                        ; linear.py:110:31
	sl_and_b64 {s[2:3], wcr}, s[2:3], s[8:9]
	.loc	1 112 20                        ; linear.py:112:20
	ml_sub_i32 v2, v6, v27
	ml_shl_b32 v2, v2, 0x1
	ml_mov_v2s_b32 s12, v2, 0x0
	ml_sub_i32 v6, v8, v27
	ml_shl_b32 v6, v6, 0x1
	ml_mov_v2s_b32 s13, v6, 0x0
	ml_add_i32 v6, s12, v20
	.loc	1 112 27 is_stmt 0              ; linear.py:112:27
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v2, v4, v0, v17
	.loc	1 112 20                        ; linear.py:112:20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[2:3], tmsk
	ml_lsa_store_dword v2, s[16:19], signed v6, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 110 31 is_stmt 1              ; linear.py:110:31
	sl_and_b64 {s[0:1], wcr}, s[0:1], s[8:9]
	.loc	1 112 27                        ; linear.py:112:27
	ml_byte_permute_b32 v0, v4, v0, v19
	.loc	1 112 20 is_stmt 0              ; linear.py:112:20
	ml_add_i32 v2, s13, v20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v0, s[16:19], signed v2, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	ml_sub_i32 v0, v5, v27
	ml_shl_b32 v0, v0, 0x1
	ml_mov_v2s_b32 s2, v0, 0x0
	ml_sub_i32 v0, v7, v27
	.loc	1 110 31 is_stmt 1              ; linear.py:110:31
	sl_and_b64 {s[0:1], wcr}, s[6:7], s[8:9]
	.loc	1 112 27                        ; linear.py:112:27
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v2, v3, v1, v17
	.loc	1 112 20 is_stmt 0              ; linear.py:112:20
	ml_shl_b32 v0, v0, 0x1
	ml_mov_v2s_b32 s3, v0, 0x0
	ml_add_i32 v0, s2, v20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v2, s[16:19], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 112 27                        ; linear.py:112:27
	ml_byte_permute_b32 v0, v3, v1, v19
	.loc	1 110 31 is_stmt 1              ; linear.py:110:31
	sl_and_b64 {s[0:1], wcr}, s[4:5], s[8:9]
	.loc	1 112 20                        ; linear.py:112:20
	ml_add_i32 v1, s3, v20
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v0, s[16:19], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 111 4                         ; linear.py:111:4
	sl_eop 
.Ltmp16:
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	linear_kernel.kd
	.type	linear_kernel.kd,@object
	.size	linear_kernel.kd, 64
linear_kernel.kd:
	.asciz	"\000\000\000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	linear_kernel@rel64-linear_kernel.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	536839
	.asciz	"\003\000\264\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	linear_kernel, .Lfunc_end0-linear_kernel
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 4352
; NumSgprs: 39
; NumVgprs: 31
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 4
; VGPRBlocks: 7
; NumSGPRsForWarpsPerNU: 35
; NumVGPRsForWarpsPerNR: 31
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
	.long	202                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0xc3 DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"linear.py"                     ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/usr/local/lib/python3.12/site-packages/flag_gems/runtime/backend/_iluvatar/ops" ; DW_AT_comp_dir
	.byte	0
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.byte	2                               ; Abbrev [2] 0x83:0x10 DW_TAG_subprogram
	.ascii	"linear_kernel"                 ; DW_AT_name
	.byte	0
	.byte	1                               ; DW_AT_inline
	.byte	3                               ; Abbrev [3] 0x93:0x3a DW_TAG_subprogram
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.long	131                             ; DW_AT_abstract_origin
	.byte	4                               ; Abbrev [4] 0xa8:0xc DW_TAG_inlined_subroutine
	.long	131                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges0                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	64                              ; DW_AT_call_line
	.byte	24                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0xb4:0xc DW_TAG_inlined_subroutine
	.long	131                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges1                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	63                              ; DW_AT_call_line
	.byte	24                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0xc0:0xc DW_TAG_inlined_subroutine
	.long	131                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges2                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	82                              ; DW_AT_call_line
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
    .group_segment_fixed_size: 0
    .kernarg_segment_align: 8
    .kernarg_segment_size: 80
    .max_flat_workgroup_size: 0
    .name:           linear_kernel
    .private_segment_fixed_size: 0
    .sgpr_count:     39
    .sgpr_spill_count: 0
    .symbol:         linear_kernel.kd
    .vgpr_count:     31
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
