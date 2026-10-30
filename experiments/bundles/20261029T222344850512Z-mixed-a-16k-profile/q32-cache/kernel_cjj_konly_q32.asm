	.text
	.globl	kernel_cjj_konly_q32            ; -- Begin function kernel_cjj_konly_q32
	.p2align	3
	.type	kernel_cjj_konly_q32,@function
	.iluvatar_kernel kernel_cjj_konly_q32
kernel_cjj_konly_q32:                   ; @kernel_cjj_konly_q32
.Lfunc_begin0:
	.file	1 "/workspace/experiments/minicpm-s2/code/native-k8-sme-mixed-20261029T205801248145Z-A/vllm_fl/patches" "biv150_konly_encoded_q32.py"
	.loc	1 34 0                          ; biv150_konly_encoded_q32.py:34:0
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
		granulated_workitem_vgpr_count = 33
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
		kernarg_segment_byte_size = 216
		workgroup_fbarrier_count = 0
		warp_sgpr_count = 104
		workitem_vgpr_count = 135
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
	sl_mov_b32 s2, tcr_lo
	sl_mov_b32 s28, tcr_lo
	ml_vrf_init_u32 v16, tcr
	ml_mov_s2v_b32 v133, s7, 0x0
.Ltmp0:
	.loc	1 168 39 prologue_end           ; biv150_konly_encoded_q32.py:168:39
	sl_lsa_load_b32x16 s[12:27], s[4:5], noreg, #64, ca
	sl_lsa_load_b32x16 s[72:87], s[4:5], noreg, #0, ca
	sl_mov_b32 s4, 0x0
.Ltmp1:
	.file	2 "/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops" "triton_attention_helpers.py"
	.loc	2 96 17                         ; triton_attention_helpers.py:96:17 @[ triton_attention_helpers.py:67:68 @[ biv150_konly_encoded_q32.py:179:73 ] ]
	sl_wait smcnt(0)
	sl_cmp_gt_i32 wcr, s22, 0x0
	sl_cbr_wcrz BB0_3, wcr
; %bb.1:                                ; %.lr.ph.preheader
	.loc	2 0 17 is_stmt 0                ; triton_attention_helpers.py:0:17
	sl_mov_b32 s3, 0xffffffff
BB0_2:                                  ; %.lr.ph
                                        ; =>This Inner Loop Header: Depth=1
	.loc	2 97 22 is_stmt 1               ; triton_attention_helpers.py:97:22 @[ triton_attention_helpers.py:67:68 @[ biv150_konly_encoded_q32.py:179:73 ] ]
	sl_add_i32 s0, s4, s22
	.loc	2 97 32 is_stmt 0               ; triton_attention_helpers.py:97:32 @[ triton_attention_helpers.py:67:68 @[ biv150_konly_encoded_q32.py:179:73 ] ]
	sl_srl_b32 {s1, wcr}, s0, 0x1f
	sl_add_i32 s0, s0, s1
	sl_sra_b32 {s8, wcr}, s0, 0x1
	.loc	2 98 44 is_stmt 1               ; triton_attention_helpers.py:98:44 @[ triton_attention_helpers.py:67:68 @[ biv150_konly_encoded_q32.py:179:73 ] ]
	sl_sra_b32 {s9, wcr}, s8, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[8:9], 0x2
	sl_add_i64 s[0:1], s[20:21], s[0:1]
	.loc	2 98 22 is_stmt 0               ; triton_attention_helpers.py:98:22 @[ triton_attention_helpers.py:67:68 @[ biv150_konly_encoded_q32.py:179:73 ] ]
	ml_lsa_load_dword v0, s[0:3], noreg, noreg, #0, ca
	.loc	2 101 11 is_stmt 1              ; triton_attention_helpers.py:101:11 @[ triton_attention_helpers.py:67:68 @[ biv150_konly_encoded_q32.py:179:73 ] ]
	sl_add_i32 s1, s8, 0x1
	.loc	2 98 22                         ; triton_attention_helpers.py:98:22 @[ triton_attention_helpers.py:67:68 @[ biv150_konly_encoded_q32.py:179:73 ] ]
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s0, v0, 0x0
	.loc	2 99 25                         ; triton_attention_helpers.py:99:25 @[ triton_attention_helpers.py:67:68 @[ biv150_konly_encoded_q32.py:179:73 ] ]
	sl_sra_b32 {s5, wcr}, s0, 0x1f
	sl_srl_b32 {s5, wcr}, s5, 0x1b
	sl_add_i32 s0, s0, s5
	sl_sra_b32 {s0, wcr}, s0, 0x5
	.loc	2 99 35 is_stmt 0               ; triton_attention_helpers.py:99:35 @[ triton_attention_helpers.py:67:68 @[ biv150_konly_encoded_q32.py:179:73 ] ]
	sl_add_i32 s0, s0, s8
	.loc	2 101 22 is_stmt 1              ; triton_attention_helpers.py:101:22 @[ triton_attention_helpers.py:67:68 @[ biv150_konly_encoded_q32.py:179:73 ] ]
	sl_cmp_gt_i32 wcr, s0, s6
	.loc	2 101 11 is_stmt 0              ; triton_attention_helpers.py:101:11 @[ triton_attention_helpers.py:67:68 @[ biv150_konly_encoded_q32.py:179:73 ] ]
	sl_csel_b32 s22, s8, s22, wcr
	sl_csel_b32 s4, s4, s1, wcr
	.loc	2 96 17 is_stmt 1               ; triton_attention_helpers.py:96:17 @[ triton_attention_helpers.py:67:68 @[ biv150_konly_encoded_q32.py:179:73 ] ]
	sl_cmp_lt_i32 wcr, s4, s22
	sl_cbr_wcrnz BB0_2, wcr
BB0_3:                                  ; %._crit_edge
	.loc	2 106 18                        ; triton_attention_helpers.py:106:18 @[ triton_attention_helpers.py:67:68 @[ biv150_konly_encoded_q32.py:179:73 ] ]
	sl_add_i32 s12, s4, 0xffffffff
.Ltmp2:
	.loc	2 69 54                         ; triton_attention_helpers.py:69:54 @[ biv150_konly_encoded_q32.py:179:73 ]
	sl_sra_b32 {s13, wcr}, s12, 0x1f
	sl_mov_b32 s3, 0xffffffff
	sl_shl_b64 {s[8:9], wcr}, s[12:13], 0x2
	sl_add_i64 s[0:1], s[20:21], s[8:9]
	.loc	2 69 32 is_stmt 0               ; triton_attention_helpers.py:69:32 @[ biv150_konly_encoded_q32.py:179:73 ]
	ml_lsa_load_dwordx2 v[0:1], s[0:3], noreg, noreg, #0, ca
	.loc	2 74 37 is_stmt 1               ; triton_attention_helpers.py:74:37 @[ biv150_konly_encoded_q32.py:179:73 ]
	sl_add_i64 s[0:1], s[84:85], s[8:9]
	.loc	2 69 32                         ; triton_attention_helpers.py:69:32 @[ biv150_konly_encoded_q32.py:179:73 ]
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s5, v0, 0x0
	.loc	2 74 22                         ; triton_attention_helpers.py:74:22 @[ biv150_konly_encoded_q32.py:179:73 ]
	ml_lsa_load_dword v0, s[0:3], noreg, noreg, #0, ca
	.loc	2 69 76                         ; triton_attention_helpers.py:69:76 @[ biv150_konly_encoded_q32.py:179:73 ]
	sl_sub_i32 s0, s6, s4
	.loc	2 72 23                         ; triton_attention_helpers.py:72:23 @[ biv150_konly_encoded_q32.py:179:73 ]
	ml_mov_v2s_b32 s1, v1, 0x0
	.loc	2 69 66                         ; triton_attention_helpers.py:69:66 @[ biv150_konly_encoded_q32.py:179:73 ]
	sl_sra_b32 {s3, wcr}, s5, 0x1f
	sl_srl_b32 {s3, wcr}, s3, 0x1b
	sl_add_i32 s3, s5, s3
	sl_srl_b32 {s3, wcr}, s3, 0x5
	.loc	2 69 76 is_stmt 0               ; triton_attention_helpers.py:69:76 @[ biv150_konly_encoded_q32.py:179:73 ]
	sl_sub_i32 s0, s0, s3
	.loc	2 70 45 is_stmt 1               ; triton_attention_helpers.py:70:45 @[ biv150_konly_encoded_q32.py:179:73 ]
	sl_mull_u32 s0, s0, 0x20
	.loc	2 73 37                         ; triton_attention_helpers.py:73:37 @[ biv150_konly_encoded_q32.py:179:73 ]
	sl_sub_i32 s94, s1, s5
.Ltmp3:
	.loc	1 182 27                        ; biv150_konly_encoded_q32.py:182:27
	sl_add_i32 s7, s0, 0x20
	.loc	1 182 38 is_stmt 0              ; biv150_konly_encoded_q32.py:182:38
	sl_cmp_lt_i32 wcr, s7, s94
.Ltmp4:
	.loc	2 74 22 is_stmt 1               ; triton_attention_helpers.py:74:22 @[ biv150_konly_encoded_q32.py:179:73 ]
	sl_wait vmcnt(0)
	ml_mov_v2s_b32 s0, v0, 0x0
.Ltmp5:
	.loc	1 182 38                        ; biv150_konly_encoded_q32.py:182:38
	sl_cbr_wcrz BB0_77, wcr
; %bb.4:
	.loc	1 0 38 is_stmt 0                ; biv150_konly_encoded_q32.py:0:38
	ml_mov_s2v_b32 v133, s0, 0x1
	ml_mov_s2v_b32 v133, s12, 0x3
	ml_mov_s2v_b32 v133, s13, 0x4
	ml_mov_s2v_b32 v133, s28, 0x5
	.loc	1 198 26 is_stmt 1              ; biv150_konly_encoded_q32.py:198:26
	sl_and_b32 {s9, wcr}, s2, 0x3c0
	sl_bfe2_b32 s4, s2, 0x86
	sl_add_i32 s6, s4, 0x10
	sl_add_i32 s8, s4, 0x20
	sl_mov_b32 s0, s4
	ml_mov_s2v_b32 v133, s0, 0x7
	sl_add_i32 s12, s4, 0x30
	.loc	1 201 56                        ; biv150_konly_encoded_q32.py:201:56
	sl_bfe2_b32 s0, s2, 0x29
	sl_mov_b32 s4, s6
	ml_mov_s2v_b32 v133, s4, 0x9
	ml_mov_s2v_b32 v133, s5, 0xa
	sl_srl_b32 {s1, wcr}, s6, 0x3
	sl_mov_b32 s4, s8
	ml_mov_s2v_b32 v133, s4, 0xb
	ml_mov_s2v_b32 v133, s5, 0xc
	sl_srl_b32 {s3, wcr}, s8, 0x3
	sl_mov_b32 s4, s12
	ml_mov_s2v_b32 v133, s4, 0xd
	ml_mov_s2v_b32 v133, s5, 0xe
	sl_srl_b32 {s4, wcr}, s12, 0x3
	sl_srl_b32 {s2, wcr}, s2, 0x9
	.loc	1 201 46 is_stmt 0              ; biv150_konly_encoded_q32.py:201:46
	sl_add_i32 s46, s7, s0
	sl_add_i32 s43, s7, s1
	sl_add_i32 s42, s7, s3
	sl_add_i32 s39, s7, s4
	sl_add_i32 s38, s46, 0x8
	sl_add_i32 s35, s46, 0xa
	sl_add_i32 s34, s46, 0xc
	ml_mov_s2v_b32 v133, s7, 0xf
	sl_add_i32 s0, s7, s2
	sl_or_b32 {s31, wcr}, s0, 0xe
	sl_add_i32 s30, s46, 0x10
	sl_add_i32 s27, s46, 0x12
	sl_add_i32 s26, s46, 0x14
	sl_or_b32 {s23, wcr}, s0, 0x16
	sl_add_i32 s22, s46, 0x18
	sl_add_i32 s19, s46, 0x1a
	sl_add_i32 s18, s46, 0x1c
	sl_or_b32 {s7, wcr}, s0, 0x1e
	.loc	1 203 52 is_stmt 1              ; biv150_konly_encoded_q32.py:203:52
	sl_add_i32 s16, s43, s5
	sl_add_i32 s20, s42, s5
	sl_add_i32 s24, s39, s5
	sl_add_i32 s28, s38, s5
	sl_add_i32 s32, s35, s5
	sl_add_i32 s36, s34, s5
	sl_add_i32 s40, s31, s5
	sl_add_i32 s50, s30, s5
	sl_add_i32 s54, s27, s5
	sl_add_i32 s58, s26, s5
	sl_add_i32 s12, s23, s5
	sl_add_i32 s8, s22, s5
	sl_add_i32 s4, s19, s5
	sl_add_i32 s2, s18, s5
	ml_mov_s2v_b32 v133, s5, 0x11
	sl_add_i32 s0, s7, s5
	ml_mov_v2s_b32 s14, v133, 0x0
	ml_mov_s2v_b32 v133, s9, 0x12
	.loc	1 204 65                        ; biv150_konly_encoded_q32.py:204:65
	sl_bfe2_b32 s3, s9, 0x66
	.loc	1 206 34                        ; biv150_konly_encoded_q32.py:206:34
	sl_sra_b32 {s17, wcr}, s16, 0x1f
	.loc	1 204 35                        ; biv150_konly_encoded_q32.py:204:35
	sl_mull_u32 s1, s14, 0x8
	.loc	1 204 56 is_stmt 0              ; biv150_konly_encoded_q32.py:204:56
	sl_add_i32 s6, s3, s1
	.loc	1 206 34 is_stmt 1              ; biv150_konly_encoded_q32.py:206:34
	sl_sra_b32 {s21, wcr}, s20, 0x1f
	sl_sra_b32 {s25, wcr}, s24, 0x1f
	sl_sra_b32 {s29, wcr}, s28, 0x1f
	sl_sra_b32 {s33, wcr}, s32, 0x1f
	sl_sra_b32 {s37, wcr}, s36, 0x1f
	sl_sra_b32 {s41, wcr}, s40, 0x1f
	sl_sra_b32 {s51, wcr}, s50, 0x1f
	sl_sra_b32 {s55, wcr}, s54, 0x1f
	sl_sra_b32 {s59, wcr}, s58, 0x1f
	sl_sra_b32 {s13, wcr}, s12, 0x1f
	sl_sra_b32 {s9, wcr}, s8, 0x1f
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_sra_b32 {s3, wcr}, s2, 0x1f
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	.loc	1 207 36                        ; biv150_konly_encoded_q32.py:207:36
	sl_mov_b32 s15, 0x0
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s46, s94
	sl_sub_bi_u64 s[44:45], s[10:11], s[10:11], wcr
	.loc	1 213 45                        ; biv150_konly_encoded_q32.py:213:45
	sl_cmp_lt_u32 wcr, s14, 0x2
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_sub_bi_u64 s[48:49], s[10:11], s[10:11], wcr
	.loc	1 213 45                        ; biv150_konly_encoded_q32.py:213:45
	sl_sub_bi_u64 s[68:69], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[48:49], s[44:45]
	.loc	1 233 24                        ; biv150_konly_encoded_q32.py:233:24
	sl_shl_b64 {s[16:17], wcr}, s[16:17], 0xc
	sl_add_i64 s[16:17], s[74:75], s[16:17]
	sl_mull_u32 s14, s6, 0x100
	sl_add_i64 s[64:65], s[16:17], s[14:15]
	sl_shl_b64 {s[16:17], wcr}, s[20:21], 0xc
	sl_add_i64 s[16:17], s[74:75], s[16:17]
	sl_add_i64 s[60:61], s[16:17], s[14:15]
	sl_shl_b64 {s[16:17], wcr}, s[24:25], 0xc
	sl_add_i64 s[16:17], s[74:75], s[16:17]
	sl_add_i64 s[56:57], s[16:17], s[14:15]
	sl_shl_b64 {s[16:17], wcr}, s[28:29], 0xc
	sl_add_i64 s[16:17], s[74:75], s[16:17]
	sl_add_i64 s[52:53], s[16:17], s[14:15]
	sl_shl_b64 {s[16:17], wcr}, s[32:33], 0xc
	sl_add_i64 s[16:17], s[74:75], s[16:17]
	sl_add_i64 s[48:49], s[16:17], s[14:15]
	sl_shl_b64 {s[16:17], wcr}, s[36:37], 0xc
	sl_add_i64 s[16:17], s[74:75], s[16:17]
	sl_add_i64 s[44:45], s[16:17], s[14:15]
	sl_shl_b64 {s[16:17], wcr}, s[40:41], 0xc
	sl_add_i64 s[16:17], s[74:75], s[16:17]
	sl_add_i64 s[40:41], s[16:17], s[14:15]
	sl_shl_b64 {s[16:17], wcr}, s[50:51], 0xc
	sl_add_i64 s[16:17], s[74:75], s[16:17]
	sl_add_i64 s[36:37], s[16:17], s[14:15]
	sl_shl_b64 {s[16:17], wcr}, s[54:55], 0xc
	sl_add_i64 s[16:17], s[74:75], s[16:17]
	sl_add_i64 s[32:33], s[16:17], s[14:15]
	sl_shl_b64 {s[16:17], wcr}, s[58:59], 0xc
	sl_add_i64 s[16:17], s[74:75], s[16:17]
	sl_add_i64 s[28:29], s[16:17], s[14:15]
	sl_shl_b64 {s[12:13], wcr}, s[12:13], 0xc
	sl_add_i64 s[12:13], s[74:75], s[12:13]
	sl_add_i64 s[24:25], s[12:13], s[14:15]
	sl_shl_b64 {s[8:9], wcr}, s[8:9], 0xc
	sl_add_i64 s[8:9], s[74:75], s[8:9]
	sl_add_i64 s[20:21], s[8:9], s[14:15]
	sl_shl_b64 {s[4:5], wcr}, s[4:5], 0xc
	sl_add_i64 s[4:5], s[74:75], s[4:5]
	sl_add_i64 s[16:17], s[4:5], s[14:15]
	sl_shl_b64 {s[2:3], wcr}, s[2:3], 0xc
	sl_add_i64 s[2:3], s[74:75], s[2:3]
	sl_add_i64 s[12:13], s[2:3], s[14:15]
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0xc
	sl_add_i64 s[0:1], s[74:75], s[0:1]
	sl_add_i64 s[0:1], s[0:1], s[14:15]
	.loc	1 233 12 is_stmt 0              ; biv150_konly_encoded_q32.py:233:12
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v1, 0x0
	sl_cbr_tcraz BB0_6, tcr
; %bb.5:
	.loc	1 203 52 is_stmt 1              ; biv150_konly_encoded_q32.py:203:52
	ml_mov_v2s_b32 s2, v133, 0x11
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	sl_mov_b32 s87, 0xfff00004
	.loc	1 203 52                        ; biv150_konly_encoded_q32.py:203:52
	sl_add_i32 s2, s46, s2
	.loc	1 206 34                        ; biv150_konly_encoded_q32.py:206:34
	sl_sra_b32 {s3, wcr}, s2, 0x1f
	.loc	1 233 24                        ; biv150_konly_encoded_q32.py:233:24
	sl_shl_b64 {s[2:3], wcr}, s[2:3], 0xc
	sl_add_i64 s[2:3], s[74:75], s[2:3]
	sl_add_i64 s[84:85], s[2:3], s[14:15]
	.loc	1 233 12 is_stmt 0              ; biv150_konly_encoded_q32.py:233:12
	ml_lsa_blkload_x1 v1, s[84:87], noreg, noreg, #0, ca
BB0_6:
	.loc	1 212 40 is_stmt 1              ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s43, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	sl_cbr_tcraz BB0_8, tcr
; %bb.7:
	sl_mov_b32 s67, 0xfff00004
	ml_lsa_blkload_x1 v0, s[64:67], noreg, noreg, #0, ca
BB0_8:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s42, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	ml_mov_b32 v2, 0x0
	ml_mov_b32 v3, 0x0
	sl_cbr_tcraz BB0_10, tcr
; %bb.9:
	sl_mov_b32 s63, 0xfff00004
	ml_lsa_blkload_x1 v3, s[60:63], noreg, noreg, #0, ca
BB0_10:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s39, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	sl_cbr_tcraz BB0_12, tcr
; %bb.11:
	sl_mov_b32 s59, 0xfff00004
	ml_lsa_blkload_x1 v2, s[56:59], noreg, noreg, #0, ca
BB0_12:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s38, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	ml_mov_b32 v4, 0x0
	ml_mov_b32 v5, 0x0
	sl_cbr_tcraz BB0_14, tcr
; %bb.13:
	sl_mov_b32 s55, 0xfff00004
	ml_lsa_blkload_x1 v5, s[52:55], noreg, noreg, #0, ca
BB0_14:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s35, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	sl_cbr_tcraz BB0_16, tcr
; %bb.15:
	sl_mov_b32 s51, 0xfff00004
	ml_lsa_blkload_x1 v4, s[48:51], noreg, noreg, #0, ca
BB0_16:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s34, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	ml_mov_b32 v6, 0x0
	ml_mov_b32 v7, 0x0
	sl_cbr_tcraz BB0_18, tcr
; %bb.17:
	sl_mov_b32 s47, 0xfff00004
	ml_lsa_blkload_x1 v7, s[44:47], noreg, noreg, #0, ca
BB0_18:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s31, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	sl_cbr_tcraz BB0_20, tcr
; %bb.19:
	sl_mov_b32 s43, 0xfff00004
	ml_lsa_blkload_x1 v6, s[40:43], noreg, noreg, #0, ca
BB0_20:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s30, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	ml_mov_b32 v8, 0x0
	ml_mov_b32 v9, 0x0
	sl_cbr_tcraz BB0_22, tcr
; %bb.21:
	sl_mov_b32 s39, 0xfff00004
	ml_lsa_blkload_x1 v9, s[36:39], noreg, noreg, #0, ca
BB0_22:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s27, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	sl_cbr_tcraz BB0_24, tcr
; %bb.23:
	sl_mov_b32 s35, 0xfff00004
	ml_lsa_blkload_x1 v8, s[32:35], noreg, noreg, #0, ca
BB0_24:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s26, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	ml_mov_b32 v10, 0x0
	ml_mov_b32 v11, 0x0
	sl_cbr_tcraz BB0_26, tcr
; %bb.25:
	sl_mov_b32 s31, 0xfff00004
	ml_lsa_blkload_x1 v11, s[28:31], noreg, noreg, #0, ca
BB0_26:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s23, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	sl_cbr_tcraz BB0_28, tcr
; %bb.27:
	sl_mov_b32 s27, 0xfff00004
	ml_lsa_blkload_x1 v10, s[24:27], noreg, noreg, #0, ca
BB0_28:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s22, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	ml_mov_b32 v12, 0x0
	ml_mov_b32 v13, 0x0
	sl_cbr_tcraz BB0_30, tcr
; %bb.29:
	sl_mov_b32 s23, 0xfff00004
	ml_lsa_blkload_x1 v13, s[20:23], noreg, noreg, #0, ca
BB0_30:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s19, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	sl_cbr_tcraz BB0_32, tcr
; %bb.31:
	sl_mov_b32 s19, 0xfff00004
	ml_lsa_blkload_x1 v12, s[16:19], noreg, noreg, #0, ca
BB0_32:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s18, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	ml_mov_b32 v14, 0x0
	ml_mov_b32 v15, 0x0
	sl_cbr_tcraz BB0_34, tcr
; %bb.33:
	sl_mov_b32 s15, 0xfff00004
	ml_lsa_blkload_x1 v15, s[12:15], noreg, noreg, #0, ca
BB0_34:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s7, s94
	sl_sub_bi_u64 s[2:3], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {tcr, wcr}, s[68:69], s[2:3]
	.loc	1 233 12                        ; biv150_konly_encoded_q32.py:233:12
	sl_cbr_tcraz BB0_36, tcr
; %bb.35:
	sl_mov_b32 s3, 0xfff00004
	ml_lsa_blkload_x1 v14, s[0:3], noreg, noreg, #0, ca
BB0_36:
.Ltmp6:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_wait vmcnt(0)
	ml_shl_b32 v17, v1, 0x10
	ml_shl_b32 v19, v0, 0x10
	ml_shl_b32 v21, v3, 0x10
	ml_shl_b32 v23, v2, 0x10
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v18, v17, 0x7fff0000
	ml_and_b32 v20, v1, 0x7fff0000
.Ltmp7:
	.file	3 "/usr/local/lib/python3.12/site-packages/triton/language" "standard.py"
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v18, v18, v20
.Ltmp8:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_xor_b32 v20, tid, 0x20
	ml_slb_shuffle_rtn_b32 v22, v18, v20
.Ltmp9:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v24, v19, 0x7fff0000
	ml_and_b32 v25, v0, 0x7fff0000
.Ltmp10:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v24, v24, v25
.Ltmp11:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v25, v24, v20
.Ltmp12:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v26, v21, 0x7fff0000
	ml_and_b32 v27, v3, 0x7fff0000
.Ltmp13:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v26, v26, v27
.Ltmp14:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v27, v26, v20
.Ltmp15:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v28, v23, 0x7fff0000
	ml_and_b32 v29, v2, 0x7fff0000
.Ltmp16:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v28, v28, v29
.Ltmp17:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v29, v28, v20
	ml_xor_b32 v32, tid, 0x8
	ml_xor_b32 v33, tid, 0x4
	ml_xor_b32 v34, tid, 0x2
	ml_xor_b32 v35, tid, 0x1
.Ltmp18:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v37, v5, 0x7fff0000
	ml_and_b32 v42, v4, 0x7fff0000
	ml_and_b32 v44, v7, 0x7fff0000
.Ltmp19:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v18, v18, v22
.Ltmp20:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_xor_b32 v22, tid, 0x10
	ml_slb_shuffle_rtn_b32 v30, v18, v22
.Ltmp21:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v46, v6, 0x7fff0000
.Ltmp22:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v24, v24, v25
.Ltmp23:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_shl_b32 v52, v9, 0x10
.Ltmp24:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v25, v24, v22
.Ltmp25:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v58, v10, 0x7fff0000
.Ltmp26:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v26, v26, v27
.Ltmp27:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v66, v12, 0x7fff0000
.Ltmp28:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v27, v26, v22
.Ltmp29:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v68, v15, 0x7fff0000
.Ltmp30:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v28, v28, v29
.Ltmp31:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v70, v14, 0x7fff0000
.Ltmp32:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v29, v28, v22
.Ltmp33:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v71, v5, 0xffff0000
	ml_and_b32 v72, v4, 0xffff0000
	ml_and_b32 v73, v7, 0xffff0000
	ml_and_b32 v74, v6, 0xffff0000
	ml_and_b32 v76, v11, 0xffff0000
	ml_and_b32 v78, v10, 0xffff0000
	ml_and_b32 v80, v13, 0xffff0000
.Ltmp34:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v18, v18, v30
.Ltmp35:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v30, v18, v32
.Ltmp36:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v86, v14, 0xffff0000
	sl_mov_b32 s0, 0x3c010204
.Ltmp37:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v24, v24, v25
.Ltmp38:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v25, v24, v32
	sl_mov_b32 s1, 0xc2fe0000
.Ltmp39:
	.loc	1 16 69                         ; biv150_konly_encoded_q32.py:16:69 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mov_b32 v88, 0x99
.Ltmp40:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v26, v26, v27
.Ltmp41:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v27, v26, v32
.Ltmp42:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v28, v28, v29
.Ltmp43:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v29, v28, v32
.Ltmp44:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v18, v18, v30
.Ltmp45:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v30, v18, v33
.Ltmp46:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v24, v24, v25
.Ltmp47:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v25, v24, v33
.Ltmp48:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v26, v26, v27
.Ltmp49:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v27, v26, v33
.Ltmp50:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v28, v28, v29
.Ltmp51:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v29, v28, v33
.Ltmp52:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v18, v18, v30
.Ltmp53:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v30, v18, v34
.Ltmp54:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v24, v24, v25
.Ltmp55:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v25, v24, v34
.Ltmp56:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v26, v26, v27
.Ltmp57:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v31, v26, v34
.Ltmp58:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_shl_b32 v27, v4, 0x10
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v40, v27, 0x7fff0000
.Ltmp59:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v28, v28, v29
.Ltmp60:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v36, v28, v34
.Ltmp61:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_shl_b32 v29, v7, 0x10
.Ltmp62:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v40, v40, v42
.Ltmp63:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v43, v29, 0x7fff0000
.Ltmp64:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v42, v40, v20
.Ltmp65:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v43, v43, v44
	sl_wait lmcnt(4)
	ml_max_i32 v18, v18, v30
.Ltmp66:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v30, v18, v35
.Ltmp67:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(4)
	ml_max_i32 v24, v24, v25
.Ltmp68:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v38, v24, v35
.Ltmp69:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_shl_b32 v25, v5, 0x10
.Ltmp70:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(4)
	ml_max_i32 v26, v26, v31
.Ltmp71:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v39, v26, v35
.Ltmp72:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_shl_b32 v31, v6, 0x10
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v45, v31, 0x7fff0000
.Ltmp73:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(4)
	ml_max_i32 v28, v28, v36
.Ltmp74:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v41, v28, v35
.Ltmp75:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v36, v25, 0x7fff0000
.Ltmp76:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v36, v36, v37
	ml_max_u32 v45, v45, v46
.Ltmp77:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v37, v36, v20
.Ltmp78:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(5)
	ml_max_i32 v40, v40, v42
.Ltmp79:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v44, v43, v20
	ml_slb_shuffle_rtn_b32 v46, v45, v20
	ml_slb_shuffle_rtn_b32 v42, v40, v22
.Ltmp80:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v36, v36, v37
.Ltmp81:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v37, v36, v22
.Ltmp82:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v43, v43, v44
.Ltmp83:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v44, v43, v22
.Ltmp84:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v45, v45, v46
.Ltmp85:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v46, v45, v22
.Ltmp86:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v40, v40, v42
.Ltmp87:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v42, v40, v32
.Ltmp88:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v36, v36, v37
.Ltmp89:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v37, v36, v32
.Ltmp90:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v43, v43, v44
.Ltmp91:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v44, v43, v32
.Ltmp92:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v45, v45, v46
.Ltmp93:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v46, v45, v32
.Ltmp94:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v40, v40, v42
.Ltmp95:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v42, v40, v33
.Ltmp96:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v36, v36, v37
.Ltmp97:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v37, v36, v33
.Ltmp98:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v43, v43, v44
.Ltmp99:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v44, v43, v33
.Ltmp100:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v45, v45, v46
.Ltmp101:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v46, v45, v33
.Ltmp102:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v40, v40, v42
.Ltmp103:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v42, v40, v34
.Ltmp104:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v36, v36, v37
.Ltmp105:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v37, v36, v34
.Ltmp106:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v43, v43, v44
.Ltmp107:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v44, v43, v34
.Ltmp108:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v46, v45, v46
.Ltmp109:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v47, v46, v34
.Ltmp110:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_shl_b32 v45, v8, 0x10
.Ltmp111:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v50, v40, v42
.Ltmp112:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v51, v50, v35
.Ltmp113:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v40, v9, 0x7fff0000
	ml_and_b32 v42, v45, 0x7fff0000
.Ltmp114:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v48, v36, v37
.Ltmp115:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v49, v48, v35
.Ltmp116:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_shl_b32 v36, v10, 0x10
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v37, v52, 0x7fff0000
.Ltmp117:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v53, v43, v44
.Ltmp118:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v54, v53, v35
.Ltmp119:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_shl_b32 v44, v11, 0x10
.Ltmp120:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v37, v37, v40
	sl_wait lmcnt(3)
	ml_max_i32 v55, v46, v47
.Ltmp121:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v56, v55, v35
.Ltmp122:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v43, v8, 0x7fff0000
.Ltmp123:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v42, v42, v43
.Ltmp124:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v46, v44, 0x7fff0000
.Ltmp125:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v40, v37, v20
.Ltmp126:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v47, v11, 0x7fff0000
.Ltmp127:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v46, v46, v47
.Ltmp128:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v57, v36, 0x7fff0000
.Ltmp129:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v43, v42, v20
.Ltmp130:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v57, v57, v58
	ml_max_i32 v10, v26, v39
	ml_max_i32 v11, v28, v41
.Ltmp131:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v47, v46, v20
	ml_slb_shuffle_rtn_b32 v58, v57, v20
.Ltmp132:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v37, v37, v40
.Ltmp133:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v40, v37, v22
.Ltmp134:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v42, v42, v43
.Ltmp135:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v43, v42, v22
.Ltmp136:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v46, v46, v47
.Ltmp137:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v47, v46, v22
.Ltmp138:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v57, v57, v58
.Ltmp139:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v58, v57, v22
.Ltmp140:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v37, v37, v40
.Ltmp141:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v40, v37, v32
.Ltmp142:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v42, v42, v43
.Ltmp143:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v43, v42, v32
.Ltmp144:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v46, v46, v47
.Ltmp145:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v47, v46, v32
.Ltmp146:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v57, v57, v58
.Ltmp147:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v58, v57, v32
.Ltmp148:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v37, v37, v40
.Ltmp149:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v40, v37, v33
.Ltmp150:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v42, v42, v43
.Ltmp151:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v43, v42, v33
.Ltmp152:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v46, v46, v47
.Ltmp153:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v47, v46, v33
.Ltmp154:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v57, v57, v58
.Ltmp155:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v58, v57, v33
.Ltmp156:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v37, v37, v40
.Ltmp157:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v40, v37, v34
.Ltmp158:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v42, v42, v43
.Ltmp159:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v43, v42, v34
.Ltmp160:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v46, v46, v47
.Ltmp161:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v47, v46, v34
.Ltmp162:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v57, v57, v58
.Ltmp163:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v58, v57, v34
.Ltmp164:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v59, v37, v40
.Ltmp165:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v60, v59, v35
.Ltmp166:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_shl_b32 v40, v15, 0x10
	ml_shl_b32 v37, v14, 0x10
.Ltmp167:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v61, v42, v43
.Ltmp168:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v62, v61, v35
.Ltmp169:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_shl_b32 v43, v13, 0x10
	ml_shl_b32 v42, v12, 0x10
.Ltmp170:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v63, v46, v47
.Ltmp171:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v64, v63, v35
.Ltmp172:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v46, v43, 0x7fff0000
	ml_and_b32 v47, v13, 0x7fff0000
.Ltmp173:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v57, v57, v58
.Ltmp174:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v58, v57, v35
.Ltmp175:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v46, v46, v47
.Ltmp176:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v65, v42, 0x7fff0000
.Ltmp177:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v65, v65, v66
.Ltmp178:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v47, v46, v20
.Ltmp179:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v67, v40, 0x7fff0000
.Ltmp180:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v67, v67, v68
.Ltmp181:
	.loc	1 13 55                         ; biv150_konly_encoded_q32.py:13:55 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v69, v37, 0x7fff0000
.Ltmp182:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v66, v65, v20
.Ltmp183:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_u32 v69, v69, v70
.Ltmp184:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v70, v0, 0xffff0000
.Ltmp185:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_i32 v13, v50, v51
.Ltmp186:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v68, v67, v20
.Ltmp187:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_i32 v14, v53, v54
.Ltmp188:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v20, v69, v20
.Ltmp189:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v46, v46, v47
.Ltmp190:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v47, v46, v22
.Ltmp191:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v65, v65, v66
.Ltmp192:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v66, v65, v22
.Ltmp193:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v67, v67, v68
.Ltmp194:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v68, v67, v22
.Ltmp195:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v20, v69, v20
.Ltmp196:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v22, v20, v22
.Ltmp197:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v69, v1, 0xffff0000
.Ltmp198:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v46, v46, v47
.Ltmp199:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v47, v46, v32
.Ltmp200:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v65, v65, v66
.Ltmp201:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v66, v65, v32
.Ltmp202:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v67, v67, v68
.Ltmp203:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v68, v67, v32
.Ltmp204:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v20, v20, v22
.Ltmp205:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v22, v20, v32
.Ltmp206:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v46, v46, v47
.Ltmp207:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v47, v46, v33
.Ltmp208:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v65, v65, v66
.Ltmp209:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v66, v65, v33
.Ltmp210:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v0, v67, v68
.Ltmp211:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v1, v0, v33
.Ltmp212:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v67, v3, 0xffff0000
	ml_and_b32 v68, v2, 0xffff0000
.Ltmp213:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v2, v20, v22
.Ltmp214:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v3, v2, v33
.Ltmp215:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_i32 v20, v61, v62
	ml_max_i32 v22, v63, v64
	sl_wait lmcnt(3)
	ml_max_i32 v4, v46, v47
.Ltmp216:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v5, v4, v34
.Ltmp217:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v47, v12, 0xffff0000
	ml_and_b32 v46, v15, 0xffff0000
.Ltmp218:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v6, v65, v66
.Ltmp219:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v7, v6, v34
.Ltmp220:
	.loc	1 12 21                         ; biv150_konly_encoded_q32.py:12:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v65, v9, 0xffff0000
	ml_and_b32 v66, v8, 0xffff0000
.Ltmp221:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v0, v0, v1
.Ltmp222:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v1, v0, v34
.Ltmp223:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_i32 v8, v18, v30
	ml_max_i32 v9, v24, v38
	sl_wait lmcnt(3)
	ml_max_i32 v2, v2, v3
.Ltmp224:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v3, v2, v34
.Ltmp225:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	ml_max_i32 v12, v48, v49
	ml_max_i32 v15, v55, v56
	ml_max_i32 v18, v59, v60
	ml_max_i32 v24, v57, v58
.Ltmp226:
	.loc	1 16 42                         ; biv150_konly_encoded_q32.py:16:42 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mov_b32 v59, 0x3f800000
.Ltmp227:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v4, v4, v5
.Ltmp228:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v5, v4, v35
.Ltmp229:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v6, v6, v7
.Ltmp230:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v7, v6, v35
.Ltmp231:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v0, v0, v1
.Ltmp232:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v1, v0, v35
.Ltmp233:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v2, v2, v3
.Ltmp234:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_slb_shuffle_rtn_b32 v3, v2, v35
.Ltmp235:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(3)
	ml_max_i32 v26, v4, v5
	sl_wait lmcnt(2)
	ml_max_i32 v28, v6, v7
	sl_wait lmcnt(1)
	ml_max_i32 v30, v0, v1
.Ltmp236:
	.loc	1 16 69                         ; biv150_konly_encoded_q32.py:16:69 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mul_f32 v0, v8, 0x3c010204
	ml_fma_f32 v1, s1, v0, v8
	ml_fma_f32 v1, s0, v1, v0
.Ltmp237:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ] ]
	sl_wait lmcnt(0)
	ml_max_i32 v38, v2, v3
.Ltmp238:
	.loc	1 16 69                         ; biv150_konly_encoded_q32.py:16:69 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_class_f32 tcr, v0, v88
	ml_csel_b32 v0, v0, v1, tcr
	ml_mul_f32 v1, v9, 0x3c010204
	ml_fma_f32 v2, s1, v1, v9
	ml_fma_f32 v2, s0, v2, v1
	ml_cmp_class_f32 tcr, v1, v88
	ml_csel_b32 v1, v1, v2, tcr
	ml_mul_f32 v2, v10, 0x3c010204
	ml_fma_f32 v3, s1, v2, v10
	ml_fma_f32 v3, s0, v3, v2
	ml_cmp_class_f32 tcr, v2, v88
	ml_csel_b32 v2, v2, v3, tcr
	ml_mul_f32 v3, v11, 0x3c010204
	ml_fma_f32 v4, s1, v3, v11
	ml_fma_f32 v4, s0, v4, v3
	ml_cmp_class_f32 tcr, v3, v88
	ml_csel_b32 v3, v3, v4, tcr
	ml_mul_f32 v4, v12, 0x3c010204
	ml_fma_f32 v5, s1, v4, v12
	ml_fma_f32 v5, s0, v5, v4
	ml_cmp_class_f32 tcr, v4, v88
	ml_csel_b32 v4, v4, v5, tcr
	ml_mul_f32 v5, v13, 0x3c010204
	ml_fma_f32 v6, s1, v5, v13
	ml_fma_f32 v6, s0, v6, v5
	ml_cmp_class_f32 tcr, v5, v88
	ml_csel_b32 v5, v5, v6, tcr
	ml_mul_f32 v6, v14, 0x3c010204
	ml_fma_f32 v7, s1, v6, v14
	ml_fma_f32 v7, s0, v7, v6
	ml_cmp_class_f32 tcr, v6, v88
	ml_csel_b32 v6, v6, v7, tcr
	ml_mul_f32 v7, v15, 0x3c010204
	ml_fma_f32 v39, s1, v7, v15
	ml_fma_f32 v39, s0, v39, v7
	ml_cmp_class_f32 tcr, v7, v88
	ml_csel_b32 v7, v7, v39, tcr
	ml_mul_f32 v39, v18, 0x3c010204
	ml_fma_f32 v41, s1, v39, v18
	ml_fma_f32 v41, s0, v41, v39
	ml_cmp_class_f32 tcr, v39, v88
	ml_csel_b32 v39, v39, v41, tcr
	ml_mul_f32 v41, v20, 0x3c010204
	ml_fma_f32 v48, s1, v41, v20
	ml_fma_f32 v48, s0, v48, v41
	ml_cmp_class_f32 tcr, v41, v88
	ml_csel_b32 v41, v41, v48, tcr
	ml_mul_f32 v48, v22, 0x3c010204
	ml_fma_f32 v49, s1, v48, v22
	ml_fma_f32 v49, s0, v49, v48
	ml_cmp_class_f32 tcr, v48, v88
	ml_csel_b32 v48, v48, v49, tcr
	ml_mul_f32 v49, v24, 0x3c010204
	ml_fma_f32 v50, s1, v49, v24
	ml_fma_f32 v50, s0, v50, v49
	ml_cmp_class_f32 tcr, v49, v88
	ml_csel_b32 v49, v49, v50, tcr
	ml_mul_f32 v50, v26, 0x3c010204
	ml_fma_f32 v51, s1, v50, v26
	ml_fma_f32 v51, s0, v51, v50
	ml_cmp_class_f32 tcr, v50, v88
	ml_csel_b32 v50, v50, v51, tcr
	ml_mul_f32 v51, v28, 0x3c010204
	ml_fma_f32 v53, s1, v51, v28
	ml_fma_f32 v53, s0, v53, v51
	ml_cmp_class_f32 tcr, v51, v88
	ml_csel_b32 v51, v51, v53, tcr
	ml_mul_f32 v53, v30, 0x3c010204
	ml_fma_f32 v54, s1, v53, v30
	ml_fma_f32 v54, s0, v54, v53
	ml_cmp_class_f32 tcr, v53, v88
	ml_csel_b32 v53, v53, v54, tcr
	ml_mul_f32 v54, v38, 0x3c010204
	ml_fma_f32 v55, s1, v54, v38
	ml_fma_f32 v55, s0, v55, v54
	ml_cmp_class_f32 tcr, v54, v88
	ml_csel_b32 v54, v54, v55, tcr
	.loc	1 16 77 is_stmt 0               ; biv150_konly_encoded_q32.py:16:77 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_max_f32 v0, v0, 0x800000
	ml_max_f32 v1, v1, 0x800000
	ml_max_f32 v2, v2, 0x800000
	ml_max_f32 v3, v3, 0x800000
	ml_max_f32 v55, v4, 0x800000
	ml_max_f32 v56, v5, 0x800000
	ml_max_f32 v57, v6, 0x800000
	ml_max_f32 v58, v7, 0x800000
	ml_max_f32 v39, v39, 0x800000
	ml_max_f32 v41, v41, 0x800000
	ml_max_f32 v48, v48, 0x800000
	ml_max_f32 v49, v49, 0x800000
	ml_max_f32 v50, v50, 0x800000
	ml_max_f32 v51, v51, 0x800000
	ml_max_f32 v53, v53, 0x800000
	ml_max_f32 v54, v54, 0x800000
	.loc	1 16 42                         ; biv150_konly_encoded_q32.py:16:42 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v8, 0x0
	ml_csel_b32 v4, v0, v59, tcr
	ml_cmp_ne_u32 tcr, v9, 0x0
	ml_csel_b32 v0, v1, v59, tcr
	ml_cmp_ne_u32 tcr, v10, 0x0
	ml_csel_b32 v5, v2, v59, tcr
	ml_cmp_ne_u32 tcr, v11, 0x0
	ml_csel_b32 v1, v3, v59, tcr
	ml_cmp_ne_u32 tcr, v12, 0x0
	ml_csel_b32 v6, v55, v59, tcr
	ml_cmp_ne_u32 tcr, v13, 0x0
	ml_csel_b32 v2, v56, v59, tcr
	ml_cmp_ne_u32 tcr, v14, 0x0
	ml_csel_b32 v7, v57, v59, tcr
	ml_cmp_ne_u32 tcr, v15, 0x0
	ml_csel_b32 v3, v58, v59, tcr
	ml_cmp_ne_u32 tcr, v18, 0x0
	ml_csel_b32 v12, v39, v59, tcr
	ml_cmp_ne_u32 tcr, v20, 0x0
	ml_csel_b32 v8, v41, v59, tcr
	ml_cmp_ne_u32 tcr, v22, 0x0
	ml_csel_b32 v13, v48, v59, tcr
	ml_cmp_ne_u32 tcr, v24, 0x0
	ml_csel_b32 v9, v49, v59, tcr
	ml_cmp_ne_u32 tcr, v26, 0x0
	ml_csel_b32 v14, v50, v59, tcr
	ml_cmp_ne_u32 tcr, v28, 0x0
	.loc	1 17 31 is_stmt 1               ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_rcp_f32 v18, v4
	.loc	1 16 42                         ; biv150_konly_encoded_q32.py:16:42 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v10, v51, v59, tcr
	ml_cmp_ne_u32 tcr, v30, 0x0
	ml_csel_b32 v15, v53, v59, tcr
	ml_cmp_ne_u32 tcr, v38, 0x0
	ml_csel_b32 v11, v54, v59, tcr
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mul_f32 v20, v17, v18
	ml_xor_b32 v22, v4, 0x80000000
	ml_fma_f32 v17, v22, v20, v17
	ml_fma_f32 v17, v17, v18, v20
	ml_cmp_class_f32 tcr, v20, v88
	ml_csel_b32 v17, v20, v17, tcr
	ml_rcp_f32 v20, v0
	ml_mul_f32 v24, v69, v18
	ml_fma_f32 v22, v22, v24, v69
	ml_fma_f32 v18, v22, v18, v24
	ml_cmp_class_f32 tcr, v24, v88
	ml_csel_b32 v18, v24, v18, tcr
	ml_mul_f32 v22, v19, v20
	ml_xor_b32 v24, v0, 0x80000000
	ml_fma_f32 v19, v24, v22, v19
	ml_fma_f32 v19, v19, v20, v22
	ml_cmp_class_f32 tcr, v22, v88
	ml_csel_b32 v19, v22, v19, tcr
	ml_rcp_f32 v22, v5
	ml_mul_f32 v26, v70, v20
	ml_fma_f32 v24, v24, v26, v70
	ml_fma_f32 v20, v24, v20, v26
	ml_cmp_class_f32 tcr, v26, v88
	ml_csel_b32 v20, v26, v20, tcr
	ml_mul_f32 v24, v21, v22
	ml_xor_b32 v26, v5, 0x80000000
	ml_fma_f32 v21, v26, v24, v21
	ml_fma_f32 v21, v21, v22, v24
	ml_cmp_class_f32 tcr, v24, v88
	ml_csel_b32 v21, v24, v21, tcr
	ml_rcp_f32 v24, v1
	ml_mul_f32 v28, v67, v22
	ml_fma_f32 v26, v26, v28, v67
	ml_fma_f32 v22, v26, v22, v28
	ml_cmp_class_f32 tcr, v28, v88
	ml_csel_b32 v22, v28, v22, tcr
	ml_mul_f32 v26, v23, v24
	ml_xor_b32 v28, v1, 0x80000000
	ml_fma_f32 v23, v28, v26, v23
	ml_fma_f32 v23, v23, v24, v26
	ml_cmp_class_f32 tcr, v26, v88
	ml_csel_b32 v23, v26, v23, tcr
	ml_rcp_f32 v26, v6
	ml_mul_f32 v30, v68, v24
	ml_fma_f32 v28, v28, v30, v68
	ml_fma_f32 v24, v28, v24, v30
	ml_cmp_class_f32 tcr, v30, v88
	ml_csel_b32 v24, v30, v24, tcr
	ml_mul_f32 v28, v25, v26
	ml_xor_b32 v30, v6, 0x80000000
	ml_fma_f32 v25, v30, v28, v25
	ml_fma_f32 v25, v25, v26, v28
	ml_cmp_class_f32 tcr, v28, v88
	ml_csel_b32 v25, v28, v25, tcr
	ml_rcp_f32 v28, v2
	ml_mul_f32 v38, v71, v26
	ml_fma_f32 v30, v30, v38, v71
	ml_fma_f32 v26, v30, v26, v38
	ml_cmp_class_f32 tcr, v38, v88
	ml_csel_b32 v26, v38, v26, tcr
	ml_mul_f32 v30, v27, v28
	ml_xor_b32 v38, v2, 0x80000000
	ml_fma_f32 v27, v38, v30, v27
	ml_fma_f32 v27, v27, v28, v30
	ml_cmp_class_f32 tcr, v30, v88
	ml_csel_b32 v27, v30, v27, tcr
	ml_rcp_f32 v30, v7
	ml_mul_f32 v39, v72, v28
	ml_fma_f32 v38, v38, v39, v72
	ml_fma_f32 v28, v38, v28, v39
	ml_cmp_class_f32 tcr, v39, v88
	ml_csel_b32 v28, v39, v28, tcr
	ml_mul_f32 v38, v29, v30
	ml_xor_b32 v39, v7, 0x80000000
	ml_fma_f32 v29, v39, v38, v29
	ml_fma_f32 v29, v29, v30, v38
	ml_cmp_class_f32 tcr, v38, v88
	ml_csel_b32 v29, v38, v29, tcr
	ml_rcp_f32 v38, v3
	ml_mul_f32 v41, v73, v30
	ml_fma_f32 v39, v39, v41, v73
	ml_fma_f32 v30, v39, v30, v41
	ml_cmp_class_f32 tcr, v41, v88
	ml_csel_b32 v30, v41, v30, tcr
	ml_mul_f32 v39, v31, v38
	ml_xor_b32 v41, v3, 0x80000000
	ml_fma_f32 v31, v41, v39, v31
	ml_fma_f32 v31, v31, v38, v39
	ml_cmp_class_f32 tcr, v39, v88
	ml_csel_b32 v31, v39, v31, tcr
	ml_rcp_f32 v48, v12
	ml_mul_f32 v39, v74, v38
	ml_fma_f32 v41, v41, v39, v74
	ml_fma_f32 v38, v41, v38, v39
	ml_cmp_class_f32 tcr, v39, v88
	ml_csel_b32 v38, v39, v38, tcr
	ml_mul_f32 v39, v52, v48
	ml_xor_b32 v41, v12, 0x80000000
	ml_fma_f32 v49, v41, v39, v52
	ml_fma_f32 v49, v49, v48, v39
	ml_cmp_class_f32 tcr, v39, v88
	ml_csel_b32 v39, v39, v49, tcr
	ml_mul_f32 v49, v65, v48
	ml_rcp_f32 v50, v8
	ml_fma_f32 v41, v41, v49, v65
	ml_fma_f32 v41, v41, v48, v49
	ml_cmp_class_f32 tcr, v49, v88
	ml_rcp_f32 v48, v13
	ml_csel_b32 v41, v49, v41, tcr
	ml_mul_f32 v49, v45, v50
	ml_xor_b32 v51, v8, 0x80000000
	ml_rcp_f32 v52, v9
	ml_fma_f32 v45, v51, v49, v45
	ml_fma_f32 v45, v45, v50, v49
	ml_cmp_class_f32 tcr, v49, v88
	ml_rcp_f32 v53, v14
	ml_csel_b32 v56, v49, v45, tcr
	ml_mul_f32 v45, v66, v50
	ml_fma_f32 v49, v51, v45, v66
	ml_rcp_f32 v51, v10
	ml_fma_f32 v49, v49, v50, v45
	ml_cmp_class_f32 tcr, v45, v88
	ml_csel_b32 v71, v45, v49, tcr
	ml_rcp_f32 v45, v15
	ml_mul_f32 v49, v44, v48
	ml_xor_b32 v50, v13, 0x80000000
	ml_fma_f32 v44, v50, v49, v44
	ml_rcp_f32 v89, v11
	ml_fma_f32 v44, v44, v48, v49
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v90, v17
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_class_f32 tcr, v49, v88
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v87, v90
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v75, v49, v44, tcr
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v91, v18
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mul_f32 v44, v76, v48
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v74, v91
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v49, v50, v44, v76
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v92, v19
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v48, v49, v48, v44
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v73, v92
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_class_f32 tcr, v44, v88
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v93, v20
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v76, v44, v48, tcr
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v72, v93
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mul_f32 v44, v36, v52
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v94, v21
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_xor_b32 v48, v9, 0x80000000
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v70, v94
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v36, v48, v44, v36
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v95, v22
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v36, v36, v52, v44
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v69, v95
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_class_f32 tcr, v44, v88
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v96, v23
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v77, v44, v36, tcr
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v68, v96
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mul_f32 v36, v78, v52
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v97, v24
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v44, v48, v36, v78
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v67, v97
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v44, v44, v52, v36
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v98, v25
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_class_f32 tcr, v36, v88
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v66, v98
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v78, v36, v44, tcr
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v36, v26
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mul_f32 v44, v43, v53
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v65, v36
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_xor_b32 v48, v14, 0x80000000
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v99, v27
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v43, v48, v44, v43
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v64, v99
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v43, v43, v53, v44
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v100, v28
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_class_f32 tcr, v44, v88
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v63, v100
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v79, v44, v43, tcr
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v101, v29
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mul_f32 v43, v80, v53
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v62, v101
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v44, v48, v43, v80
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v102, v30
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v44, v44, v53, v43
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v61, v102
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_class_f32 tcr, v43, v88
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v103, v31
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v80, v43, v44, tcr
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v60, v103
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mul_f32 v43, v42, v51
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v104, v38
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_xor_b32 v44, v10, 0x80000000
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v59, v104
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v42, v44, v43, v42
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v105, v39
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v42, v42, v51, v43
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v58, v105
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_class_f32 tcr, v43, v88
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v106, v41
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v81, v43, v42, tcr
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v57, v106
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mul_f32 v42, v47, v51
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v107, v56
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v43, v44, v42, v47
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v55, v107
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v43, v43, v51, v42
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v108, v71
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_class_f32 tcr, v42, v88
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v54, v108
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v82, v42, v43, tcr
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v109, v75
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mul_f32 v42, v40, v45
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v53, v109
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_xor_b32 v43, v15, 0x80000000
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v110, v76
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v40, v43, v42, v40
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v52, v110
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v40, v40, v45, v42
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v111, v77
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_class_f32 tcr, v42, v88
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v51, v111
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v83, v42, v40, tcr
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v40, v78
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mul_f32 v42, v46, v45
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v50, v40
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v43, v43, v42, v46
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v112, v79
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v43, v43, v45, v42
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v49, v112
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_class_f32 tcr, v42, v88
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v113, v80
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v84, v42, v43, tcr
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v48, v113
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mul_f32 v42, v37, v89
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v114, v81
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_xor_b32 v43, v11, 0x80000000
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v47, v114
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v37, v43, v42, v37
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v115, v82
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v37, v37, v89, v42
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v46, v115
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_class_f32 tcr, v42, v88
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v116, v83
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v85, v42, v37, tcr
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v45, v116
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mul_f32 v37, v86, v89
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v117, v84
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v42, v43, v37, v86
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v44, v117
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_fma_f32 v42, v42, v89, v37
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v89, v85
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_class_f32 tcr, v37, v88
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v43, v89
	.loc	1 17 31                         ; biv150_konly_encoded_q32.py:17:31 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v86, v37, v42, tcr
	.loc	1 18 23                         ; biv150_konly_encoded_q32.py:18:23 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_abs_f32 v37, v86
	.loc	1 20 27                         ; biv150_konly_encoded_q32.py:20:27 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v88, v90, v87
	.loc	1 19 21                         ; biv150_konly_encoded_q32.py:19:21 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_floor_f32 v42, v37
	.loc	1 20 27                         ; biv150_konly_encoded_q32.py:20:27 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v90, v91, v74
	ml_sub_f32 v91, v92, v73
	ml_sub_f32 v92, v93, v72
	ml_sub_f32 v93, v94, v70
	ml_sub_f32 v94, v95, v69
	ml_sub_f32 v95, v96, v68
	ml_sub_f32 v96, v97, v67
	ml_sub_f32 v97, v98, v66
	ml_sub_f32 v36, v36, v65
	ml_sub_f32 v98, v99, v64
	ml_sub_f32 v99, v100, v63
	ml_sub_f32 v100, v101, v62
	ml_sub_f32 v101, v102, v61
	ml_sub_f32 v102, v103, v60
	ml_sub_f32 v103, v104, v59
	ml_sub_f32 v104, v105, v58
	ml_sub_f32 v105, v106, v57
	ml_sub_f32 v106, v107, v55
	ml_sub_f32 v107, v108, v54
	ml_sub_f32 v108, v109, v53
	ml_sub_f32 v109, v110, v52
	ml_sub_f32 v110, v111, v51
	ml_sub_f32 v40, v40, v50
	ml_sub_f32 v111, v112, v49
	ml_sub_f32 v112, v113, v48
	ml_sub_f32 v113, v114, v47
	ml_sub_f32 v114, v115, v46
	ml_sub_f32 v115, v116, v45
	ml_sub_f32 v116, v117, v44
	ml_sub_f32 v89, v89, v43
	ml_sub_f32 v117, v37, v42
	.loc	1 21 28                         ; biv150_konly_encoded_q32.py:21:28 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_gt_f32 tcr, v88, 0x3f000000
.Ltmp239:
	.loc	1 199 26                        ; biv150_konly_encoded_q32.py:199:26
	ml_and_b32 v37, tid, 0xf
.Ltmp240:
	.loc	1 21 28                         ; biv150_konly_encoded_q32.py:21:28 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x14
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x15
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v90, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x16
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x17
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v91, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x18
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x19
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v92, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x1a
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x1b
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v93, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x1c
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x1d
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v94, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x1e
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x1f
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v95, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x20
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x21
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v96, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x22
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x23
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v97, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x24
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x25
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v36, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x26
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x27
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v98, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x28
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x29
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v99, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x2a
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x2b
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v100, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x2c
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x2d
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v101, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x2e
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x2f
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v102, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x30
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x31
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v103, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x32
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x33
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v104, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x34
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x35
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v105, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x36
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x37
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v106, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x38
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x39
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v107, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x3a
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x3b
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v108, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x3c
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x3d
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v109, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x3e
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x3f
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v110, 0x3f000000
	ml_mov_v2s_b32 s87, v133, 0x12
.Ltmp241:
	.loc	1 201 46                        ; biv150_konly_encoded_q32.py:201:46
	ml_mov_v2s_b32 s1, v133, 0xf
.Ltmp242:
	.loc	1 21 28                         ; biv150_konly_encoded_q32.py:21:28 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v134, s98, 0x0
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v134, s98, 0x1
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v40, 0x3f000000
.Ltmp243:
	.loc	1 201 56                        ; biv150_konly_encoded_q32.py:201:56
	sl_srl_b32 {s0, wcr}, s87, 0x5
	.loc	1 201 46 is_stmt 0              ; biv150_konly_encoded_q32.py:201:46
	sl_add_i32 s0, s1, s0
	sl_add_i32 s16, s0, 0x1
.Ltmp244:
	.loc	1 21 28 is_stmt 1               ; biv150_konly_encoded_q32.py:21:28 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v134, s98, 0x2
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v134, s98, 0x3
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v111, 0x3f000000
.Ltmp245:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s0, s94
.Ltmp246:
	.loc	1 21 28                         ; biv150_konly_encoded_q32.py:21:28 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v134, s98, 0x4
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v134, s98, 0x5
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v112, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v134, s98, 0x6
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v134, s98, 0x7
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v113, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v134, s98, 0x8
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v134, s98, 0x9
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v114, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v134, s98, 0xa
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v134, s98, 0xb
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v115, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v134, s98, 0xc
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v134, s98, 0xd
	sl_mov_b32 s98, 0xffffffff
	ml_cmp_gt_f32 tcr, v116, 0x3f000000
	sl_mov_b64 s[64:65], tcr
	ml_cmp_gt_f32 tcr, v89, 0x3f000000
	sl_mov_b64 s[66:67], tcr
	ml_cmp_gt_f32 tcr, v117, 0x3f000000
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v134, s98, 0xe
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v134, s98, 0xf
	sl_mov_b32 s98, 0xffffffff
	.loc	1 21 49 is_stmt 0               ; biv150_konly_encoded_q32.py:21:49 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_eq_f32 tcr, v88, 0x3f000000
	ml_mov_s2v_b32 v134, s0, 0x10
.Ltmp247:
	.loc	1 212 40 is_stmt 1              ; biv150_konly_encoded_q32.py:212:40
	sl_sub_bi_u64 s[0:1], s[10:11], s[10:11], wcr
	ml_mov_s2v_b32 v134, s16, 0x11
.Ltmp248:
	.loc	1 21 49                         ; biv150_konly_encoded_q32.py:21:49 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 s[44:45], tcr
	ml_cmp_eq_f32 tcr, v90, 0x3f000000
.Ltmp249:
	.loc	1 212 40                        ; biv150_konly_encoded_q32.py:212:40
	sl_cmp_lt_i32 wcr, s16, s94
	sl_sub_bi_u64 s[74:75], s[10:11], s[10:11], wcr
	.loc	1 234 61                        ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {s[0:1], wcr}, s[68:69], s[0:1]
.Ltmp250:
	.loc	1 21 49                         ; biv150_konly_encoded_q32.py:21:49 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 s[42:43], tcr
	ml_cmp_eq_f32 tcr, v91, 0x3f000000
	.loc	1 21 67 is_stmt 0               ; biv150_konly_encoded_q32.py:21:67 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mov_s2v_b32 v134, s0, 0x12
	ml_mov_s2v_b32 v134, s1, 0x13
	sl_reg_read s0, hwreg(HW_REG_MODE)
	.loc	1 21 49                         ; biv150_konly_encoded_q32.py:21:49 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 s[40:41], tcr
	ml_cmp_eq_f32 tcr, v92, 0x3f000000
.Ltmp251:
	.loc	1 234 61 is_stmt 1              ; biv150_konly_encoded_q32.py:234:61
	sl_and_b64 {s[16:17], wcr}, s[68:69], s[74:75]
	ml_mov_s2v_b32 v134, s16, 0x14
	ml_mov_s2v_b32 v134, s17, 0x15
.Ltmp252:
	.loc	1 21 49                         ; biv150_konly_encoded_q32.py:21:49 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 s[38:39], tcr
	ml_cmp_eq_f32 tcr, v93, 0x3f000000
	.loc	1 21 67 is_stmt 0               ; biv150_konly_encoded_q32.py:21:67 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b32 {s1, wcr}, s0, 0x3
	.loc	1 21 49                         ; biv150_konly_encoded_q32.py:21:49 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 s[36:37], tcr
	ml_cmp_eq_f32 tcr, v94, 0x3f000000
	sl_mov_b64 s[34:35], tcr
	ml_cmp_eq_f32 tcr, v95, 0x3f000000
	sl_mov_b64 s[32:33], tcr
	ml_cmp_eq_f32 tcr, v96, 0x3f000000
	sl_mov_b64 s[30:31], tcr
	ml_cmp_eq_f32 tcr, v97, 0x3f000000
	sl_mov_b64 s[28:29], tcr
	ml_cmp_eq_f32 tcr, v36, 0x3f000000
.Ltmp253:
	.loc	1 208 10 is_stmt 1              ; biv150_konly_encoded_q32.py:208:10
	ml_mov_b32 v36, 0x0
.Ltmp254:
	.loc	1 21 49                         ; biv150_konly_encoded_q32.py:21:49 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 s[26:27], tcr
	ml_cmp_eq_f32 tcr, v98, 0x3f000000
	sl_mov_b64 s[24:25], tcr
	ml_cmp_eq_f32 tcr, v99, 0x3f000000
	sl_mov_b64 s[2:3], tcr
	ml_cmp_eq_f32 tcr, v100, 0x3f000000
	sl_mov_b64 s[4:5], tcr
	ml_cmp_eq_f32 tcr, v101, 0x3f000000
	sl_mov_b64 s[18:19], tcr
	ml_cmp_eq_f32 tcr, v102, 0x3f000000
	sl_mov_b64 s[6:7], tcr
	ml_cmp_eq_f32 tcr, v103, 0x3f000000
	sl_mov_b64 s[14:15], tcr
	ml_cmp_eq_f32 tcr, v104, 0x3f000000
	sl_mov_b64 s[12:13], tcr
	ml_cmp_eq_f32 tcr, v105, 0x3f000000
	sl_mov_b64 s[8:9], tcr
	ml_cmp_eq_f32 tcr, v106, 0x3f000000
	sl_mov_b64 s[46:47], tcr
	ml_cmp_eq_f32 tcr, v107, 0x3f000000
	sl_mov_b64 s[48:49], tcr
	ml_cmp_eq_f32 tcr, v108, 0x3f000000
	sl_mov_b64 s[92:93], tcr
	ml_cmp_eq_f32 tcr, v109, 0x3f000000
	sl_mov_b64 s[90:91], tcr
	ml_cmp_eq_f32 tcr, v110, 0x3f000000
	sl_mov_b64 s[88:89], tcr
	ml_cmp_eq_f32 tcr, v40, 0x3f000000
.Ltmp255:
	.loc	1 198 26                        ; biv150_konly_encoded_q32.py:198:26
	ml_and_b32 v40, tid, 0x30
.Ltmp256:
	.loc	1 21 49                         ; biv150_konly_encoded_q32.py:21:49 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 s[58:59], tcr
	ml_cmp_eq_f32 tcr, v111, 0x3f000000
	sl_mov_b64 s[56:57], tcr
	ml_cmp_eq_f32 tcr, v112, 0x3f000000
	sl_mov_b64 s[54:55], tcr
	ml_cmp_eq_f32 tcr, v113, 0x3f000000
	sl_mov_b64 s[50:51], tcr
	ml_cmp_eq_f32 tcr, v114, 0x3f000000
	sl_mov_b64 s[60:61], tcr
	ml_cmp_eq_f32 tcr, v115, 0x3f000000
	sl_mov_b64 s[84:85], tcr
	ml_cmp_eq_f32 tcr, v116, 0x3f000000
	sl_mov_b64 s[70:71], tcr
	ml_cmp_eq_f32 tcr, v89, 0x3f000000
	sl_mov_b64 s[62:63], tcr
	ml_cmp_eq_f32 tcr, v117, 0x3f000000
	sl_mov_b64 s[52:53], tcr
	.loc	1 21 67 is_stmt 0               ; biv150_konly_encoded_q32.py:21:67 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v88, v87
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v89, v74
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v90, v73
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v91, v72
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v92, v70
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v93, v69
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v94, v68
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v95, v67
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v96, v66
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v97, v65
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v98, v64
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v99, v63
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v100, v62
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v101, v61
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v102, v60
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v103, v59
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v104, v58
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v105, v57
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v106, v55
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v107, v54
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v108, v53
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v109, v52
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v110, v51
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v111, v50
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v112, v49
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v113, v48
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v114, v47
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v115, v46
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v116, v45
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v117, v44
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v118, v43
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v119, v42
	sl_reg_write hwreg(HW_REG_MODE), s0
	.loc	1 21 79                         ; biv150_konly_encoded_q32.py:21:79 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v88, v88, 0x1
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v88, 0x0
	.loc	1 21 79                         ; biv150_konly_encoded_q32.py:21:79 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v88, v89, 0x1
	ml_and_b32 v89, v90, 0x1
	ml_and_b32 v90, v91, 0x1
	ml_and_b32 v91, v92, 0x1
	ml_and_b32 v92, v93, 0x1
	ml_and_b32 v93, v94, 0x1
	ml_and_b32 v94, v95, 0x1
	ml_and_b32 v95, v96, 0x1
	ml_and_b32 v96, v97, 0x1
	ml_and_b32 v97, v98, 0x1
	ml_and_b32 v98, v99, 0x1
	ml_and_b32 v99, v100, 0x1
	ml_and_b32 v100, v101, 0x1
	ml_and_b32 v101, v102, 0x1
	ml_and_b32 v102, v103, 0x1
	ml_and_b32 v103, v104, 0x1
	ml_and_b32 v104, v105, 0x1
	ml_and_b32 v105, v106, 0x1
	ml_and_b32 v106, v107, 0x1
	ml_and_b32 v107, v108, 0x1
	ml_and_b32 v108, v109, 0x1
	ml_and_b32 v109, v110, 0x1
	ml_and_b32 v110, v111, 0x1
	ml_and_b32 v111, v112, 0x1
	ml_and_b32 v112, v113, 0x1
	ml_and_b32 v113, v114, 0x1
	ml_and_b32 v114, v115, 0x1
	ml_and_b32 v115, v116, 0x1
	ml_and_b32 v116, v117, 0x1
	ml_and_b32 v117, v118, 0x1
	ml_and_b32 v118, v119, 0x1
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[44:45], wcr}, s[44:45], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v88, 0x0
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[42:43], wcr}, s[42:43], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v89, 0x0
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[40:41], wcr}, s[40:41], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v90, 0x0
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[38:39], wcr}, s[38:39], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v91, 0x0
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[16:17], wcr}, s[36:37], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v92, 0x0
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[34:35], wcr}, s[34:35], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v93, 0x0
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[20:21], wcr}, s[32:33], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v94, 0x0
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[22:23], wcr}, s[30:31], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v95, 0x0
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[28:29], wcr}, s[28:29], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v96, 0x0
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[26:27], wcr}, s[26:27], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v97, 0x0
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[68:69], wcr}, s[24:25], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v98, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mov_v2s_b32 s24, v133, 0x20
	ml_mov_v2s_b32 s25, v133, 0x21
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[30:31], wcr}, s[2:3], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v99, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[20:21], wcr}, s[24:25], s[20:21]
	ml_mov_v2s_b32 s24, v133, 0x22
	ml_mov_v2s_b32 s25, v133, 0x23
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[32:33], wcr}, s[4:5], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v100, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[22:23], wcr}, s[24:25], s[22:23]
	ml_mov_v2s_b32 s24, v133, 0x24
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[74:75], wcr}, s[18:19], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v101, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mov_v2s_b32 s18, v133, 0x1c
	ml_mov_v2s_b32 s19, v133, 0x1d
	ml_mov_v2s_b32 s25, v133, 0x25
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[36:37], wcr}, s[6:7], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v102, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[16:17], wcr}, s[18:19], s[16:17]
	ml_mov_v2s_b32 s18, v133, 0x1e
	ml_mov_v2s_b32 s19, v133, 0x1f
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[6:7], wcr}, s[14:15], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v103, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mov_v2s_b32 s14, v133, 0x1a
	ml_mov_v2s_b32 s15, v133, 0x1b
	sl_or_b64 {s[18:19], wcr}, s[18:19], s[34:35]
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[4:5], wcr}, s[12:13], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v104, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mov_v2s_b32 s12, v133, 0x18
	ml_mov_v2s_b32 s13, v133, 0x19
	sl_or_b64 {s[14:15], wcr}, s[14:15], s[38:39]
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[2:3], wcr}, s[8:9], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v105, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mov_v2s_b32 s8, v133, 0x14
	ml_mov_v2s_b32 s9, v133, 0x15
	sl_or_b64 {s[12:13], wcr}, s[12:13], s[40:41]
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[46:47], wcr}, s[46:47], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v106, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[24:25], wcr}, s[24:25], s[28:29]
	ml_mov_v2s_b32 s28, v133, 0x26
	ml_mov_v2s_b32 s29, v133, 0x27
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[48:49], wcr}, s[48:49], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v107, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mov_v2s_b32 s34, v133, 0x2a
	sl_or_b64 {s[26:27], wcr}, s[28:29], s[26:27]
	ml_mov_v2s_b32 s28, v133, 0x28
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[92:93], wcr}, s[92:93], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v108, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mov_v2s_b32 s29, v133, 0x29
	ml_mov_v2s_b32 s35, v133, 0x2b
	ml_mov_v2s_b32 s38, v133, 0x30
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[90:91], wcr}, s[90:91], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v109, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[28:29], wcr}, s[28:29], s[68:69]
	sl_or_b64 {s[30:31], wcr}, s[34:35], s[30:31]
	ml_mov_v2s_b32 s34, v133, 0x2c
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[88:89], wcr}, s[88:89], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v110, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mov_v2s_b32 s35, v133, 0x2d
	ml_mov_v2s_b32 s39, v133, 0x31
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[58:59], wcr}, s[58:59], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v111, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[32:33], wcr}, s[34:35], s[32:33]
	ml_mov_v2s_b32 s34, v133, 0x2e
	ml_mov_v2s_b32 s35, v133, 0x2f
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[56:57], wcr}, s[56:57], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v112, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[36:37], wcr}, s[38:39], s[36:37]
	sl_or_b64 {s[34:35], wcr}, s[34:35], s[74:75]
	ml_mov_v2s_b32 s38, v133, 0x32
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[54:55], wcr}, s[54:55], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v113, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mov_v2s_b32 s39, v133, 0x33
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[50:51], wcr}, s[50:51], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v114, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[38:39], wcr}, s[38:39], s[6:7]
	ml_mov_v2s_b32 s6, v133, 0x34
	ml_mov_v2s_b32 s7, v133, 0x35
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[60:61], wcr}, s[60:61], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v115, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[40:41], wcr}, s[6:7], s[4:5]
	ml_mov_v2s_b32 s4, v133, 0x36
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[84:85], wcr}, s[84:85], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v116, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_mov_v2s_b32 s5, v133, 0x37
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[0:1], wcr}, s[70:71], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v117, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[64:65], wcr}, s[64:65], s[0:1]
	ml_mov_v2s_b32 s0, v134, 0xe
	ml_mov_v2s_b32 s1, v134, 0xf
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[62:63], wcr}, s[62:63], tcr
	.loc	1 21 85                         ; biv150_konly_encoded_q32.py:21:85 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_ne_u32 tcr, v118, 0x0
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[66:67], wcr}, s[66:67], s[62:63]
	.loc	1 21 57                         ; biv150_konly_encoded_q32.py:21:57 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b64 {s[52:53], wcr}, s[52:53], tcr
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {tcr, wcr}, s[8:9], s[44:45]
	ml_mov_v2s_b32 s8, v133, 0x16
	ml_mov_v2s_b32 s9, v133, 0x17
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v88, 1, v36, tcr
	ml_cvt_f32_i32  v88, v88
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v87, v87, v88
	.loc	1 21 36 is_stmt 1               ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[8:9], wcr}, s[8:9], s[42:43]
	sl_or_b64 {s[42:43], wcr}, s[4:5], s[2:3]
	ml_mov_v2s_b32 s2, v133, 0x38
	ml_mov_v2s_b32 s3, v133, 0x39
	ml_mov_v2s_b32 s4, v134, 0x2
	ml_mov_v2s_b32 s5, v134, 0x3
	.loc	1 22 35                         ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[8:9]
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[44:45], wcr}, s[2:3], s[46:47]
	ml_mov_v2s_b32 s2, v133, 0x3a
	ml_mov_v2s_b32 s3, v133, 0x3b
	sl_or_b64 {s[68:69], wcr}, s[4:5], s[58:59]
	ml_mov_v2s_b32 s4, v134, 0x4
	ml_mov_v2s_b32 s5, v134, 0x5
	sl_or_b64 {s[46:47], wcr}, s[2:3], s[48:49]
	ml_mov_v2s_b32 s2, v133, 0x3c
	ml_mov_v2s_b32 s3, v133, 0x3d
	sl_or_b64 {s[6:7], wcr}, s[4:5], s[56:57]
	ml_mov_v2s_b32 s4, v134, 0x6
	ml_mov_v2s_b32 s5, v134, 0x7
	sl_or_b64 {s[70:71], wcr}, s[2:3], s[92:93]
	ml_mov_v2s_b32 s2, v133, 0x3e
	ml_mov_v2s_b32 s3, v133, 0x3f
	sl_or_b64 {s[56:57], wcr}, s[4:5], s[54:55]
	ml_mov_v2s_b32 s4, v134, 0x8
	ml_mov_v2s_b32 s5, v134, 0x9
	sl_or_b64 {s[48:49], wcr}, s[2:3], s[90:91]
	ml_mov_v2s_b32 s2, v134, 0x0
	ml_mov_v2s_b32 s3, v134, 0x1
	sl_or_b64 {s[58:59], wcr}, s[4:5], s[50:51]
	ml_mov_v2s_b32 s4, v134, 0xa
	ml_mov_v2s_b32 s5, v134, 0xb
	sl_or_b64 {s[2:3], wcr}, s[2:3], s[88:89]
	.loc	1 22 35                         ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v89, 1, v36, tcr
	sl_mov_b64 tcr, s[12:13]
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[60:61], wcr}, s[4:5], s[60:61]
	ml_mov_v2s_b32 s4, v134, 0xc
	ml_mov_v2s_b32 s5, v134, 0xd
	.loc	1 22 35                         ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_csel_b32 v90, 1, v36, tcr
	sl_mov_b64 tcr, s[14:15]
	ml_csel_b32 v91, 1, v36, tcr
	.loc	1 21 36                         ; biv150_konly_encoded_q32.py:21:36 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b64 {s[50:51], wcr}, s[4:5], s[84:85]
	sl_or_b64 {s[4:5], wcr}, s[0:1], s[52:53]
	.loc	1 22 35                         ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[16:17]
	ml_csel_b32 v92, 1, v36, tcr
	sl_mov_b64 tcr, s[18:19]
	ml_csel_b32 v93, 1, v36, tcr
	sl_mov_b64 tcr, s[20:21]
	ml_csel_b32 v94, 1, v36, tcr
	sl_mov_b64 tcr, s[22:23]
	ml_csel_b32 v95, 1, v36, tcr
	sl_mov_b64 tcr, s[24:25]
	ml_csel_b32 v96, 1, v36, tcr
	sl_mov_b64 tcr, s[26:27]
	ml_csel_b32 v97, 1, v36, tcr
	sl_mov_b64 tcr, s[28:29]
	ml_csel_b32 v98, 1, v36, tcr
	sl_mov_b64 tcr, s[30:31]
	ml_csel_b32 v99, 1, v36, tcr
	sl_mov_b64 tcr, s[32:33]
	ml_csel_b32 v100, 1, v36, tcr
	sl_mov_b64 tcr, s[34:35]
	ml_csel_b32 v101, 1, v36, tcr
	sl_mov_b64 tcr, s[36:37]
	ml_csel_b32 v102, 1, v36, tcr
	sl_mov_b64 tcr, s[38:39]
	ml_csel_b32 v103, 1, v36, tcr
	sl_mov_b64 tcr, s[40:41]
	ml_csel_b32 v104, 1, v36, tcr
	sl_mov_b64 tcr, s[42:43]
	ml_csel_b32 v105, 1, v36, tcr
	sl_mov_b64 tcr, s[44:45]
	ml_csel_b32 v106, 1, v36, tcr
	sl_mov_b64 tcr, s[46:47]
	ml_csel_b32 v107, 1, v36, tcr
	sl_mov_b64 tcr, s[70:71]
	ml_csel_b32 v108, 1, v36, tcr
	sl_mov_b64 tcr, s[48:49]
	ml_csel_b32 v109, 1, v36, tcr
	sl_mov_b64 tcr, s[2:3]
	ml_csel_b32 v110, 1, v36, tcr
	sl_mov_b64 tcr, s[68:69]
	ml_csel_b32 v111, 1, v36, tcr
	sl_mov_b64 tcr, s[6:7]
	ml_csel_b32 v112, 1, v36, tcr
	sl_mov_b64 tcr, s[56:57]
	ml_csel_b32 v113, 1, v36, tcr
	sl_mov_b64 tcr, s[58:59]
	ml_csel_b32 v114, 1, v36, tcr
	sl_mov_b64 tcr, s[60:61]
	ml_csel_b32 v115, 1, v36, tcr
	sl_mov_b64 tcr, s[50:51]
	ml_csel_b32 v116, 1, v36, tcr
	sl_mov_b64 tcr, s[64:65]
	ml_csel_b32 v117, 1, v36, tcr
	sl_mov_b64 tcr, s[66:67]
	ml_csel_b32 v118, 1, v36, tcr
	sl_mov_b64 tcr, s[4:5]
	ml_csel_b32 v88, 1, v36, tcr
	.loc	1 23 33                         ; biv150_konly_encoded_q32.py:23:33 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cmp_lt_f32 tcr, v17, 0x0
	.loc	1 23 37 is_stmt 0               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v17, 0, v87
	.loc	1 24 60 is_stmt 1               ; biv150_konly_encoded_q32.py:24:60 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_reg_read s0, hwreg(HW_REG_MODE)
	.loc	1 23 33                         ; biv150_konly_encoded_q32.py:23:33 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 s[68:69], tcr
	ml_cmp_lt_f32 tcr, v18, 0x0
	.loc	1 22 35                         ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v18, v89
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v18, v74, v18
	.loc	1 24 60 is_stmt 1               ; biv150_konly_encoded_q32.py:24:60 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_or_b32 {s1, wcr}, s0, 0x3
	.loc	1 23 33                         ; biv150_konly_encoded_q32.py:23:33 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 s[66:67], tcr
	ml_cmp_lt_f32 tcr, v19, 0x0
	.loc	1 23 37 is_stmt 0               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v19, 0, v18
	.loc	1 23 33                         ; biv150_konly_encoded_q32.py:23:33 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 s[64:65], tcr
	ml_cmp_lt_f32 tcr, v20, 0x0
	sl_mov_b64 s[62:63], tcr
	ml_cmp_lt_f32 tcr, v21, 0x0
	sl_mov_b64 s[60:61], tcr
	ml_cmp_lt_f32 tcr, v22, 0x0
	sl_mov_b64 s[58:59], tcr
	ml_cmp_lt_f32 tcr, v23, 0x0
	sl_mov_b64 s[56:57], tcr
	ml_cmp_lt_f32 tcr, v24, 0x0
	sl_mov_b64 s[54:55], tcr
	ml_cmp_lt_f32 tcr, v25, 0x0
	sl_mov_b64 s[52:53], tcr
	ml_cmp_lt_f32 tcr, v26, 0x0
	sl_mov_b64 s[50:51], tcr
	ml_cmp_lt_f32 tcr, v27, 0x0
	sl_mov_b64 s[48:49], tcr
	ml_cmp_lt_f32 tcr, v28, 0x0
	sl_mov_b64 s[46:47], tcr
	ml_cmp_lt_f32 tcr, v29, 0x0
	sl_mov_b64 s[44:45], tcr
	ml_cmp_lt_f32 tcr, v30, 0x0
	sl_mov_b64 s[42:43], tcr
	ml_cmp_lt_f32 tcr, v31, 0x0
	sl_mov_b64 s[40:41], tcr
	ml_cmp_lt_f32 tcr, v38, 0x0
	sl_mov_b64 s[38:39], tcr
	ml_cmp_lt_f32 tcr, v39, 0x0
	sl_mov_b64 s[36:37], tcr
	ml_cmp_lt_f32 tcr, v41, 0x0
	sl_mov_b64 s[34:35], tcr
	ml_cmp_lt_f32 tcr, v56, 0x0
	sl_mov_b64 s[32:33], tcr
	ml_cmp_lt_f32 tcr, v71, 0x0
	sl_mov_b64 s[30:31], tcr
	ml_cmp_lt_f32 tcr, v75, 0x0
	sl_mov_b64 s[28:29], tcr
	ml_cmp_lt_f32 tcr, v76, 0x0
	sl_mov_b64 s[26:27], tcr
	ml_cmp_lt_f32 tcr, v77, 0x0
	sl_mov_b64 s[24:25], tcr
	ml_cmp_lt_f32 tcr, v78, 0x0
	sl_mov_b64 s[22:23], tcr
	ml_cmp_lt_f32 tcr, v79, 0x0
	sl_mov_b64 s[20:21], tcr
	ml_cmp_lt_f32 tcr, v80, 0x0
	sl_mov_b64 s[18:19], tcr
	ml_cmp_lt_f32 tcr, v81, 0x0
	sl_mov_b64 s[16:17], tcr
	ml_cmp_lt_f32 tcr, v82, 0x0
	sl_mov_b64 s[14:15], tcr
	ml_cmp_lt_f32 tcr, v83, 0x0
	sl_mov_b64 s[12:13], tcr
	ml_cmp_lt_f32 tcr, v84, 0x0
	sl_mov_b64 s[8:9], tcr
	ml_cmp_lt_f32 tcr, v85, 0x0
	sl_mov_b64 s[70:71], tcr
	ml_cmp_lt_f32 tcr, v86, 0x0
	sl_mov_b64 s[4:5], tcr
	.loc	1 23 46                         ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[68:69]
	ml_csel_b32 v17, v17, v87, tcr
	sl_mov_b64 tcr, s[66:67]
	ml_csel_b32 v18, v19, v18, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v19, v90
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v19, v73, v19
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v20, 0, v19
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[64:65]
	ml_csel_b32 v19, v20, v19, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v20, v91
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v20, v72, v20
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v21, 0, v20
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[62:63]
	ml_csel_b32 v20, v21, v20, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v21, v92
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v21, v70, v21
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v22, 0, v21
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[60:61]
	ml_csel_b32 v21, v22, v21, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v22, v93
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v22, v69, v22
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v23, 0, v22
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[58:59]
	ml_csel_b32 v22, v23, v22, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v23, v94
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v23, v68, v23
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v24, 0, v23
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[56:57]
	ml_csel_b32 v23, v24, v23, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v24, v95
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v24, v67, v24
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v25, 0, v24
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[54:55]
	ml_csel_b32 v24, v25, v24, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v25, v96
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v25, v66, v25
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v26, 0, v25
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[52:53]
	ml_csel_b32 v25, v26, v25, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v26, v97
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v26, v65, v26
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v27, 0, v26
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[50:51]
	ml_csel_b32 v26, v27, v26, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v27, v98
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v27, v64, v27
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v28, 0, v27
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[48:49]
	ml_csel_b32 v27, v28, v27, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v28, v99
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v28, v63, v28
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v29, 0, v28
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[46:47]
	ml_csel_b32 v28, v29, v28, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v29, v100
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v29, v62, v29
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v30, 0, v29
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[44:45]
	ml_csel_b32 v29, v30, v29, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v30, v101
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v30, v61, v30
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v31, 0, v30
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[42:43]
	ml_csel_b32 v30, v31, v30, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v31, v102
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v31, v60, v31
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v38, 0, v31
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[40:41]
	ml_csel_b32 v31, v38, v31, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v38, v103
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v38, v59, v38
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v39, 0, v38
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[38:39]
	ml_csel_b32 v38, v39, v38, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v39, v104
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v39, v58, v39
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v41, 0, v39
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[36:37]
	ml_csel_b32 v39, v41, v39, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v41, v105
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v41, v57, v41
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v41
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[34:35]
	ml_csel_b32 v41, v56, v41, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v56, v106
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v55, v55, v56
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v55
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[32:33]
	ml_csel_b32 v55, v56, v55, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v56, v107
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v54, v54, v56
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v54
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[30:31]
	ml_csel_b32 v54, v56, v54, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v56, v108
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v53, v53, v56
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v53
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[28:29]
	ml_csel_b32 v53, v56, v53, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v56, v109
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v52, v52, v56
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v52
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[26:27]
	ml_csel_b32 v52, v56, v52, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v56, v110
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v51, v51, v56
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v51
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[24:25]
	ml_csel_b32 v51, v56, v51, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v56, v111
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v50, v50, v56
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v50
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[22:23]
	ml_csel_b32 v50, v56, v50, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v56, v112
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v49, v49, v56
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v49
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[20:21]
	ml_csel_b32 v49, v56, v49, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v56, v113
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v48, v48, v56
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v48
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[18:19]
	ml_csel_b32 v48, v56, v48, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v56, v114
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v47, v47, v56
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v47
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[16:17]
	ml_csel_b32 v47, v56, v47, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v56, v115
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v46, v46, v56
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v46
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[14:15]
	ml_csel_b32 v46, v56, v46, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v56, v116
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v45, v45, v56
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v45
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[12:13]
	ml_csel_b32 v45, v56, v45, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v56, v117
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v44, v44, v56
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v44
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[8:9]
	ml_csel_b32 v44, v56, v44, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v56, v118
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v43, v43, v56
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v43
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[70:71]
	ml_csel_b32 v43, v56, v43, tcr
	.loc	1 22 35 is_stmt 1               ; biv150_konly_encoded_q32.py:22:35 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_cvt_f32_i32  v56, v88
	.loc	1 22 22 is_stmt 0               ; biv150_konly_encoded_q32.py:22:22 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_add_f32 v42, v42, v56
	.loc	1 23 37 is_stmt 1               ; biv150_konly_encoded_q32.py:23:37 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_sub_f32 v56, 0, v42
	.loc	1 23 46 is_stmt 0               ; biv150_konly_encoded_q32.py:23:46 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_mov_b64 tcr, s[4:5]
	ml_csel_b32 v42, v56, v42, tcr
	.loc	1 24 48 is_stmt 1               ; biv150_konly_encoded_q32.py:24:48 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_max_f32 v17, v17, 0xc2fe0000
	ml_max_f32 v18, v18, 0xc2fe0000
	ml_max_f32 v19, v19, 0xc2fe0000
	ml_max_f32 v20, v20, 0xc2fe0000
	ml_max_f32 v21, v21, 0xc2fe0000
	ml_max_f32 v22, v22, 0xc2fe0000
	ml_max_f32 v23, v23, 0xc2fe0000
	ml_max_f32 v24, v24, 0xc2fe0000
	ml_max_f32 v25, v25, 0xc2fe0000
	ml_max_f32 v26, v26, 0xc2fe0000
	ml_max_f32 v27, v27, 0xc2fe0000
	ml_max_f32 v28, v28, 0xc2fe0000
	ml_max_f32 v29, v29, 0xc2fe0000
	ml_max_f32 v30, v30, 0xc2fe0000
	ml_max_f32 v31, v31, 0xc2fe0000
	ml_max_f32 v38, v38, 0xc2fe0000
	ml_max_f32 v39, v39, 0xc2fe0000
	ml_max_f32 v41, v41, 0xc2fe0000
	ml_max_f32 v55, v55, 0xc2fe0000
	ml_max_f32 v54, v54, 0xc2fe0000
	ml_max_f32 v53, v53, 0xc2fe0000
	ml_max_f32 v52, v52, 0xc2fe0000
	ml_max_f32 v51, v51, 0xc2fe0000
	ml_max_f32 v50, v50, 0xc2fe0000
	ml_max_f32 v49, v49, 0xc2fe0000
	ml_max_f32 v48, v48, 0xc2fe0000
	ml_max_f32 v47, v47, 0xc2fe0000
	ml_max_f32 v46, v46, 0xc2fe0000
	ml_max_f32 v45, v45, 0xc2fe0000
	ml_max_f32 v44, v44, 0xc2fe0000
	ml_max_f32 v43, v43, 0xc2fe0000
	ml_max_f32 v42, v42, 0xc2fe0000
	.loc	1 24 29 is_stmt 0               ; biv150_konly_encoded_q32.py:24:29 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_min_f32 v17, v17, 0x42fe0000
	ml_min_f32 v18, v18, 0x42fe0000
	ml_min_f32 v19, v19, 0x42fe0000
	ml_min_f32 v20, v20, 0x42fe0000
	ml_min_f32 v21, v21, 0x42fe0000
	ml_min_f32 v22, v22, 0x42fe0000
	ml_min_f32 v23, v23, 0x42fe0000
	ml_min_f32 v24, v24, 0x42fe0000
	ml_min_f32 v25, v25, 0x42fe0000
	ml_min_f32 v26, v26, 0x42fe0000
	ml_min_f32 v27, v27, 0x42fe0000
	ml_min_f32 v28, v28, 0x42fe0000
	ml_min_f32 v29, v29, 0x42fe0000
	ml_min_f32 v30, v30, 0x42fe0000
	ml_min_f32 v31, v31, 0x42fe0000
	ml_min_f32 v38, v38, 0x42fe0000
	ml_min_f32 v39, v39, 0x42fe0000
	ml_min_f32 v41, v41, 0x42fe0000
	ml_min_f32 v55, v55, 0x42fe0000
	ml_min_f32 v54, v54, 0x42fe0000
	ml_min_f32 v53, v53, 0x42fe0000
	ml_min_f32 v52, v52, 0x42fe0000
	ml_min_f32 v51, v51, 0x42fe0000
	ml_min_f32 v50, v50, 0x42fe0000
	ml_min_f32 v49, v49, 0x42fe0000
	ml_min_f32 v48, v48, 0x42fe0000
	ml_min_f32 v47, v47, 0x42fe0000
	ml_min_f32 v46, v46, 0x42fe0000
	ml_min_f32 v45, v45, 0x42fe0000
	ml_min_f32 v44, v44, 0x42fe0000
	ml_min_f32 v43, v43, 0x42fe0000
	ml_min_f32 v42, v42, 0x42fe0000
	.loc	1 24 60                         ; biv150_konly_encoded_q32.py:24:60 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v17, v17
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v18, v18
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v19, v19
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v20, v20
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v21, v21
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v22, v22
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v23, v23
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v24, v24
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v25, v25
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v26, v26
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v27, v27
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v28, v28
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v29, v29
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v30, v30
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v31, v31
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v38, v38
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v39, v39
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v41, v41
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v55, v55
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v54, v54
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v53, v53
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v52, v52
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v51, v51
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v50, v50
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v49, v49
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v48, v48
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v47, v47
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v46, v46
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v45, v45
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v44, v44
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v43, v43
	sl_reg_write hwreg(HW_REG_MODE), s0
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v42, v42
	sl_reg_write hwreg(HW_REG_MODE), s0
	ml_shl_b32 v40, v40, 0x5
	ml_and_b32 v56, tid, 0x7
	ml_shl_b32 v56, v56, 0x2
	ml_mov_v2s_b32 s1, v133, 0x5
	ml_and_b32 v57, tid, 0x8
	ml_cmp_eq_u32 tcr, v57, 0x0
	ml_mov_b32 v57, 0x140
	sl_and_b32 {s4, wcr}, s1, 0x380
	sl_srl_b32 {s0, wcr}, s4, 0x2
	ml_csel_b32 v57, 0, v57, tcr
	ml_xor_b32 v57, s0, v57
	ml_anyop3_b32 v40, v57, v56, v40, 0xfffffffe
	sl_bfe2_b32 s5, s1, 0x26
	ml_slb_store_b8  v17, v40, s5, #0, null
	sl_add_i32 s0, s5, 0x800
.Ltmp257:
	.loc	1 403 60 is_stmt 1              ; biv150_konly_encoded_q32.py:403:60
	sl_mov_b32 s2, 0x8000
.Ltmp258:
	.loc	1 24 60                         ; biv150_konly_encoded_q32.py:24:60 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_slb_store_b8  v18, v40, s5, #2, null
	ml_slb_store_b8  v19, v40, s0, #0, null
	ml_slb_store_b8  v20, v40, s0, #2, null
	sl_add_i32 s0, s5, 0x1000
	ml_slb_store_b8  v21, v40, s0, #0, null
	ml_slb_store_b8  v22, v40, s0, #2, null
	sl_add_i32 s0, s5, 0x1800
	ml_slb_store_b8  v23, v40, s0, #0, null
	ml_slb_store_b8  v24, v40, s0, #2, null
	sl_add_i32 s0, s5, 0x2000
	ml_slb_store_b8  v25, v40, s0, #0, null
	ml_slb_store_b8  v26, v40, s0, #2, null
	sl_add_i32 s0, s5, 0x2800
	ml_slb_store_b8  v27, v40, s0, #0, null
	ml_slb_store_b8  v28, v40, s0, #2, null
	sl_add_i32 s0, s5, 0x3000
	ml_slb_store_b8  v29, v40, s0, #0, null
	ml_slb_store_b8  v30, v40, s0, #2, null
	sl_add_i32 s0, s5, 0x3800
	ml_slb_store_b8  v31, v40, s0, #0, null
	ml_slb_store_b8  v38, v40, s0, #2, null
	sl_add_i32 s0, s5, 0x4000
	ml_slb_store_b8  v39, v40, s0, #0, null
	ml_slb_store_b8  v41, v40, s0, #2, null
	sl_add_i32 s0, s5, 0x4800
	ml_slb_store_b8  v55, v40, s0, #0, null
	ml_slb_store_b8  v54, v40, s0, #2, null
	sl_add_i32 s0, s5, 0x5000
	ml_slb_store_b8  v53, v40, s0, #0, null
	ml_slb_store_b8  v52, v40, s0, #2, null
	sl_add_i32 s0, s5, 0x5800
	ml_slb_store_b8  v51, v40, s0, #0, null
	ml_slb_store_b8  v50, v40, s0, #2, null
	sl_add_i32 s0, s5, 0x6000
	ml_slb_store_b8  v49, v40, s0, #0, null
	ml_slb_store_b8  v48, v40, s0, #2, null
	sl_add_i32 s0, s5, 0x6800
	ml_slb_store_b8  v47, v40, s0, #0, null
	ml_slb_store_b8  v46, v40, s0, #2, null
	sl_add_i32 s0, s5, 0x7000
	ml_slb_store_b8  v45, v40, s0, #0, null
	ml_slb_store_b8  v44, v40, s0, #2, null
	sl_add_i32 s0, s5, 0x7800
	ml_slb_store_b8  v43, v40, s0, #0, null
	ml_slb_store_b8  v42, v40, s0, #2, null
.Ltmp259:
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	sl_srl_b32 {s0, wcr}, s87, 0x1
	ml_mov_b32 v17, s0
.Ltmp260:
	.loc	1 24 60                         ; biv150_konly_encoded_q32.py:24:60 @[ biv150_konly_encoded_q32.py:238:48 ]
	sl_and_b32 {s0, wcr}, s1, 0x40
.Ltmp261:
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	ml_slb_store_b32x4  v[4:7], v17, s2, #0, null
.Ltmp262:
	.loc	2 181 10                        ; triton_attention_helpers.py:181:10 @[ biv150_konly_encoded_q32.py:281:8 ]
	ml_mov_v2s_b32 s1, v133, 0xf
.Ltmp263:
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	ml_slb_store_b32x4  v[0:3], v17, s2, #512, null
	ml_slb_store_b32x4  v[12:15], v17, s2, #16, null
	ml_slb_store_b32x4  v[8:11], v17, s2, #528, null
	sl_nop 0x0
	ml_mov_v2s_b32 s2, v133, 0x1
	.loc	1 254 28                        ; biv150_konly_encoded_q32.py:254:28
	sl_sub_i32 s7, s2, s94
.Ltmp264:
	.loc	2 181 10                        ; triton_attention_helpers.py:181:10 @[ biv150_konly_encoded_q32.py:281:8 ]
	sl_add_i32 s1, s1, s7
	.loc	2 183 10                        ; triton_attention_helpers.py:183:10 @[ biv150_konly_encoded_q32.py:281:8 ]
	sl_add_i32 s1, s1, 0x20
	.loc	2 191 60                        ; triton_attention_helpers.py:191:60 @[ biv150_konly_encoded_q32.py:281:8 ]
	sl_min_i32 s40, s1, s2
.Ltmp265:
	.loc	2 24 20                         ; triton_attention_helpers.py:24:20 @[ triton_attention_helpers.py:193:44 @[ biv150_konly_encoded_q32.py:281:8 ] ]
	sl_add_i32 s8, s40, 0x3f
.Ltmp266:
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	sl_wait lmcnt(0)
	sl_barrier 
	.loc	1 285 28                        ; biv150_konly_encoded_q32.py:285:28
	sl_cmp_gt_i32 wcr, s8, 0x3f
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	sl_mull_u32 s6, s0, 0x8
	.loc	1 285 28                        ; biv150_konly_encoded_q32.py:285:28
	sl_cbr_wcrz BB0_59, wcr
; %bb.37:                               ; %.lr.ph108
	.loc	1 0 28 is_stmt 0                ; biv150_konly_encoded_q32.py:0:28
	sl_mov_b32 s98, tcr_lo
	ml_mov_s2v_b32 v133, s98, 0x1
	sl_mov_b32 s98, 0xffffffff
	sl_mov_b32 s98, tcr_hi
	ml_mov_s2v_b32 v133, s98, 0x2
	sl_mov_b32 s98, 0xffffffff
	.loc	1 198 26 is_stmt 1              ; biv150_konly_encoded_q32.py:198:26
	ml_and_b32 v0, tid, 0x30
	.loc	1 0 0 is_stmt 0                 ; biv150_konly_encoded_q32.py:0
	ml_shl_b32 v1, v0, 0x1
	sl_srl_b32 {s0, wcr}, s4, 0x5
	.loc	1 403 60 is_stmt 1              ; biv150_konly_encoded_q32.py:403:60
	sl_add_i32 s0, s6, s0
	sl_add_i32 s2, s0, 0x8000
	ml_slb_load_b32x1  v41, v1, s2, #0, null
	.loc	1 199 26                        ; biv150_konly_encoded_q32.py:199:26
	ml_and_b32 v2, tid, 0xf
	ml_shl_b32 v43, v2, 0x1
	ml_mov_b32 v3, 0x280
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	ml_slb_load_b32x1  v42, v1, s2, #128, null
	ml_csel_b32 v3, 0, v3, tcr
	.loc	1 290 31                        ; biv150_konly_encoded_q32.py:290:31
	ml_mov_v2s_b32 s0, v133, 0x3
	ml_mov_v2s_b32 s1, v133, 0x4
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	ml_slb_load_b32x1  v44, v1, s2, #256, null
	.loc	1 200 26                        ; biv150_konly_encoded_q32.py:200:26
	ml_bfe2_b32 v48, v16, 0xa5
	ml_mov_v2s_b32 s14, v133, 0x0
	.loc	1 290 31                        ; biv150_konly_encoded_q32.py:290:31
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0xf
	sl_add_i64 s[42:43], s[82:83], s[0:1]
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	ml_slb_load_b32x1  v47, v1, s2, #384, null
	.loc	1 199 26                        ; biv150_konly_encoded_q32.py:199:26
	ml_shl_b32 v1, v16, 0x2
	sl_mov_b32 s33, 0x0
	.loc	1 335 32                        ; biv150_konly_encoded_q32.py:335:32
	sl_mull_u32 s32, s14, 0x80
	.loc	1 285 28                        ; biv150_konly_encoded_q32.py:285:28
	sl_mull_u32 s0, s14, 0x100
	sl_mov_b32 s1, s33
	sl_add_i64 s[82:83], s[80:81], s[0:1]
	sl_add_i64 s[0:1], s[76:77], s[32:33]
	.loc	1 382 38                        ; biv150_konly_encoded_q32.py:382:38
	ml_mov_s2v_b32 v133, s0, 0xf
	ml_mov_s2v_b32 v133, s1, 0x10
	ml_mov_v2s_b32 s75, v134, 0x11
	ml_mov_v2s_b32 s0, v134, 0x10
.Ltmp267:
	.loc	2 24 26                         ; triton_attention_helpers.py:24:26 @[ triton_attention_helpers.py:193:44 @[ biv150_konly_encoded_q32.py:281:8 ] ]
	sl_srl_b32 {s8, wcr}, s8, 0x6
	ml_shl_b32 v38, v16, 0x1
.Ltmp268:
	.loc	1 382 38                        ; biv150_konly_encoded_q32.py:382:38
	sl_add_i32 s6, s75, s7
	sl_add_i32 s18, s0, s7
	ml_mov_v2s_b32 s0, v38, 0x0
	ml_shl_b32 v4, v16, 0x6
	ml_and_b32 v5, v4, 0x4c0
	ml_and_b32 v1, v1, 0x830
	sl_and_b32 {s0, wcr}, s0, 0x300
	ml_srl_b32 v6, v16, 0x3
	ml_and_b32 v6, v6, 0x3c
	ml_add_i32 v6, s0, v6
	ml_anyop3_b32 v49, v5, v1, v6, 0x1e
	ml_shl_b32 v1, v0, 0x6
.Ltmp269:
	.loc	1 24 60                         ; biv150_konly_encoded_q32.py:24:60 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v5, tid, 0x7
	ml_shl_b32 v5, v5, 0x3
	sl_srl_b32 {s0, wcr}, s4, 0x1
	ml_xor_b32 v3, s0, v3
	sl_add_i32 s66, s5, s5
	sl_mull_u32 s0, s87, 0x20
	ml_shl_b32 v0, v0, 0x2
	ml_anyop3_b32 v50, s0, v0, v43, 0xfffffffe
	ml_xor_b32 v51, v50, 0x40
	ml_shl_b32 v0, tid, 0x2
	sl_mov_b32 s0, 0x300
	ml_anyop3_b32 v52, s0, v4, v0, 0xfffffff8
	ml_xor_b32 v53, v52, 0x10
	ml_xor_b32 v54, v52, 0x20
	ml_xor_b32 v55, v52, 0x30
	ml_and_b32 v4, tid, 0x10
	ml_cmp_eq_u32 tcr, v4, 0x0
	ml_mov_b32 v6, 0x7632
	ml_mov_b32 v7, 0x5410
	ml_csel_b32 v56, v7, v6, tcr
	ml_csel_b32 v57, v6, v7, tcr
	ml_shl_b32 v4, v4, 0x1
	ml_and_b32 v8, tid, 0x20
	ml_cmp_eq_u32 tcr, v8, 0x0
	ml_mov_b32 v9, 0x1054
	ml_csel_b32 v58, v7, v9, tcr
	ml_mov_b32 v7, 0x3276
	ml_csel_b32 v59, v6, v7, tcr
	ml_srl_b32 v6, v8, 0x1
	ml_anyop3_b32 v60, v4, v6, v2, 0xfffffffe
	ml_xor_b32 v61, v60, 0x10
	ml_xor_b32 v62, v0, 0x80
	ml_mov_v2s_b32 s0, v133, 0x7
	ml_mov_v2s_b32 s1, v133, 0x8
.Ltmp270:
	.loc	1 285 28                        ; biv150_konly_encoded_q32.py:285:28
	sl_mov_b32 s1, s33
	sl_mov_b32 s41, s33
	ml_mov_v2s_b32 s2, v133, 0x9
	ml_mov_v2s_b32 s3, v133, 0xa
	sl_mov_b32 s3, s33
	sl_sra_b32 {s67, wcr}, s6, 0x1f
	ml_mov_s2v_b32 v133, s2, 0x9
	ml_mov_s2v_b32 v133, s3, 0xa
	ml_mov_v2s_b32 s2, v133, 0xb
	ml_mov_v2s_b32 s3, v133, 0xc
	sl_mov_b32 s3, s33
	sl_sra_b32 {s68, wcr}, s18, 0x1f
	ml_mov_s2v_b32 v133, s2, 0xb
	ml_mov_s2v_b32 v133, s3, 0xc
	ml_mov_v2s_b32 s2, v133, 0xd
	ml_mov_v2s_b32 s3, v133, 0xe
	sl_mov_b32 s3, s33
	sl_mov_b32 s9, s33
	ml_mov_s2v_b32 v133, s2, 0xd
	ml_mov_s2v_b32 v133, s3, 0xe
	ml_mov_s2v_b32 v133, s8, 0x5
	ml_mov_s2v_b32 v133, s9, 0x6
	ml_mov_s2v_b32 v133, s0, 0x7
	ml_mov_s2v_b32 v133, s1, 0x8
	sl_mull_u32 s50, s0, 0x200
	sl_mov_b32 s51, s33
	ml_shl_b32 v63, v2, 0x3
	ml_and_b32 v0, v16, 0x1f
	sl_mov_b32 s0, 0x3c0
	ml_anyop3_b32 v64, s0, v38, v0, 0xfffffff8
	sl_sub_u64 s[52:53], s[10:11], s[10:11]
	ml_mov_b32 v65, 0x0
	ml_mov_b32 v66, 0xff800000
	sl_mov_b32 s15, 0xffffffff
	sl_mov_b32 s1, 0x3fffffff
	sl_mov_b32 s0, 0xfffffff4
	sl_mov_b32 s56, 0xfffffffc
	ml_mov_s2v_b32 v133, s0, 0x12
	ml_mov_s2v_b32 v133, s1, 0x13
	sl_mov_b32 s57, s1
	sl_mov_b32 s19, 0xfff00004
	ml_anyop3_b32 v67, v3, v5, v1, 0xfffffffe
	sl_mov_b32 s70, 0x504
	sl_mov_b32 s71, 0x60504
	sl_mov_b32 s76, 0x1000504
	sl_mov_b32 s77, 0x2010200
	sl_mov_b32 s80, 0xc000
	sl_mov_b32 s81, 0xd000
	sl_mov_b32 s44, 0xc400
	sl_mov_b32 s74, 0xc800
	sl_mov_b32 s84, 0xcc00
	sl_mov_b32 s85, 0xd400
	sl_mov_b32 s88, 0xd800
	sl_mov_b32 s89, 0xdc00
	sl_mov_b32 s90, 0x400
	sl_mov_b32 s91, 0x9000
	sl_mov_b32 s92, 0xa000
	sl_mov_b32 s93, 0xb000
	sl_mov_b32 s94, 0x8400
	sl_mov_b32 s4, 0x9400
	sl_mov_b32 s5, 0xa400
	sl_mov_b32 s87, 0xb400
	sl_mov_b32 s46, 0x8800
	sl_mov_b32 s47, 0x9800
	sl_mov_b32 s69, 0xa800
	sl_mov_b32 s7, 0xb800
	sl_mov_b32 s48, 0x8c00
	sl_mov_b32 s49, 0x9c00
	sl_mov_b32 s54, 0xac00
	sl_mov_b32 s55, 0xbc00
	ml_mov_b32 v45, 0x0
	ml_mov_b32 v46, 0x0
	ml_mov_b32 v39, 0x0
	ml_mov_b32 v40, 0x0
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
	ml_mov_b32 v71, 0xff800000
	ml_mov_b32 v70, 0xff800000
	ml_mov_b32 v69, 0xff800000
	ml_mov_b32 v68, 0xff800000
	sl_jump BB0_39
BB0_38:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 0 28 is_stmt 0                ; biv150_konly_encoded_q32.py:0:28
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 347 16 is_stmt 1              ; biv150_konly_encoded_q32.py:347:16
	ml_slb_load_b32x1  v88, v52, s80, #0, null
.Ltmp271:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	ml_cmp_ge_u32 tcr, s18, v75
	ml_mov_v2s_b32 s2, v134, 0x14
	ml_mov_v2s_b32 s3, v134, 0x15
.Ltmp272:
	.loc	1 347 16                        ; biv150_konly_encoded_q32.py:347:16
	ml_slb_load_b32x1  v96, v52, s44, #0, null
.Ltmp273:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_mov_b64 s[8:9], tcr
.Ltmp274:
	.loc	1 347 16                        ; biv150_konly_encoded_q32.py:347:16
	ml_slb_load_b32x1  v92, v52, s74, #0, null
	ml_slb_load_b32x1  v98, v52, s84, #0, null
	ml_slb_load_b32x1  v100, v52, s81, #0, null
	ml_slb_load_b32x1  v102, v52, s85, #0, null
	ml_slb_load_b32x1  v104, v52, s88, #0, null
	ml_slb_load_b32x1  v106, v52, s89, #0, null
	ml_slb_load_b32x1  v89, v53, s80, #0, null
	ml_slb_load_b32x1  v97, v53, s44, #0, null
	ml_slb_load_b32x1  v93, v53, s74, #0, null
	ml_slb_load_b32x1  v99, v53, s84, #0, null
	ml_slb_load_b32x1  v101, v53, s81, #0, null
	ml_slb_load_b32x1  v103, v53, s85, #0, null
	ml_slb_load_b32x1  v105, v53, s88, #0, null
	ml_slb_load_b32x1  v107, v53, s89, #0, null
	ml_slb_load_b32x1  v108, v54, s80, #0, null
	ml_slb_load_b32x1  v110, v54, s44, #0, null
	ml_slb_load_b32x1  v111, v54, s74, #0, null
	ml_slb_load_b32x1  v113, v54, s84, #0, null
	ml_slb_load_b32x1  v114, v54, s81, #0, null
	ml_slb_load_b32x1  v116, v54, s85, #0, null
	ml_slb_load_b32x1  v117, v54, s88, #0, null
	ml_slb_load_b32x1  v109, v55, s80, #0, null
	ml_slb_load_b32x1  v112, v55, s74, #0, null
	ml_slb_load_b32x1  v115, v55, s81, #0, null
	ml_slb_load_b32x1  v118, v55, s88, #0, null
	.loc	1 402 12                        ; biv150_konly_encoded_q32.py:402:12
	ml_slb_load_b8  v80, v50, noreg, #0, null
	ml_slb_load_b8  v81, v50, noreg, #1, null
	ml_slb_load_b8  v82, v50, noreg, #32, null
	ml_slb_load_b8  v83, v50, noreg, #33, null
	ml_slb_load_b8  v84, v51, noreg, #256, null
	ml_slb_load_b8  v85, v51, noreg, #257, null
	ml_slb_load_b8  v86, v51, noreg, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v80, v81, v80, 4
	ml_mov_b32 v81, v36
	ml_slb_load_b8  v87, v51, noreg, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v80, v82, v80, s70
	ml_mov_b32 v82, v36
	ml_slb_load_b8  v121, v51, noreg, #768, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v119, v83, v80, s71
	ml_mov_b32 v83, v36
	ml_slb_load_b8  v122, v51, noreg, #769, null
	ml_slb_load_b8  v123, v51, noreg, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v80, v85, v84, 4
	ml_slb_load_b8  v124, v51, noreg, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v80, v86, v80, s70
	ml_slb_load_b8  v125, v50, noreg, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v120, v87, v80, s71
	ml_mov_b32 v80, 0x0
	ml_slb_load_b8  v126, v50, noreg, #513, null
	ml_matrix_mad_i32_i8_m16n16k32 v[84:87], v[119:120], v[88:89], v[80:83]
	ml_slb_load_b8  v127, v50, noreg, #544, null
	ml_matrix_mad_i32_i8_m16n16k32 v[88:91], v[119:120], v[92:93], v[80:83]
	ml_slb_load_b8  v128, v50, noreg, #545, null
	ml_matrix_mad_i32_i8_m16n16k32 v[92:95], v[119:120], v[100:101], v[80:83]
	ml_slb_load_b8  v129, v51, s90, #256, null
	ml_matrix_mad_i32_i8_m16n16k32 v[80:83], v[119:120], v[104:105], v[80:83]
	ml_slb_load_b8  v130, v51, s90, #257, null
	sl_wait lmcnt(8)
	ml_byte_permute_b32 v100, v122, v121, 4
	sl_wait lmcnt(7)
	ml_byte_permute_b32 v100, v123, v100, s70
	ml_slb_load_b8  v131, v51, s90, #288, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v101, v126, v125, 4
	ml_slb_load_b8  v132, v51, s90, #289, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v119, v127, v101, s70
	ml_byte_permute_b32 v101, v124, v100, s71
	ml_slb_load_b8  v104, v50, s90, #0, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v100, v128, v119, s71
	ml_slb_load_b8  v105, v50, s90, #1, null
	ml_matrix_mad_i32_i8_m16n16k32 v[84:87], v[100:101], v[108:109], v[84:87]
	ml_slb_load_b8  v119, v50, s90, #32, null
	ml_matrix_mad_i32_i8_m16n16k32 v[88:91], v[100:101], v[111:112], v[88:91]
	ml_slb_load_b8  v108, v50, s90, #33, null
	ml_matrix_mad_i32_i8_m16n16k32 v[92:95], v[100:101], v[114:115], v[92:95]
	ml_slb_load_b8  v109, v51, s90, #768, null
	ml_matrix_mad_i32_i8_m16n16k32 v[80:83], v[100:101], v[117:118], v[80:83]
	ml_slb_load_b8  v112, v51, s90, #769, null
	sl_wait lmcnt(8)
	ml_byte_permute_b32 v100, v130, v129, 4
	sl_wait lmcnt(7)
	ml_byte_permute_b32 v100, v131, v100, s70
	ml_slb_load_b8  v114, v51, s90, #800, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v101, v105, v104, 4
	ml_slb_load_b8  v115, v51, s90, #801, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v104, v119, v101, s70
	ml_byte_permute_b32 v101, v132, v100, s71
	ml_slb_load_b8  v105, v50, s90, #512, null
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v100, v108, v104, s71
	ml_slb_load_b8  v104, v50, s90, #513, null
	ml_matrix_mad_i32_i8_m16n16k32 v[84:87], v[100:101], v[96:97], v[84:87]
	ml_slb_load_b8  v97, v50, s90, #544, null
	ml_matrix_mad_i32_i8_m16n16k32 v[88:91], v[100:101], v[98:99], v[88:91]
	ml_slb_load_b8  v98, v50, s90, #545, null
	ml_matrix_mad_i32_i8_m16n16k32 v[92:95], v[100:101], v[102:103], v[92:95]
	.loc	1 347 16                        ; biv150_konly_encoded_q32.py:347:16
	ml_slb_load_b32x1  v111, v55, s44, #0, null
	.loc	1 402 12                        ; biv150_konly_encoded_q32.py:402:12
	ml_matrix_mad_i32_i8_m16n16k32 v[80:83], v[100:101], v[106:107], v[80:83]
	.loc	1 347 16                        ; biv150_konly_encoded_q32.py:347:16
	ml_slb_load_b32x1  v96, v54, s89, #0, null
	.loc	1 402 12                        ; biv150_konly_encoded_q32.py:402:12
	sl_wait lmcnt(8)
	ml_byte_permute_b32 v99, v112, v109, 4
	sl_wait lmcnt(7)
	ml_byte_permute_b32 v99, v114, v99, s70
	sl_wait lmcnt(6)
	ml_byte_permute_b32 v99, v115, v99, s71
	sl_wait lmcnt(4)
	ml_byte_permute_b32 v100, v104, v105, 4
	.loc	1 347 16                        ; biv150_konly_encoded_q32.py:347:16
	ml_slb_load_b32x1  v114, v55, s84, #0, null
	.loc	1 402 12                        ; biv150_konly_encoded_q32.py:402:12
	sl_wait lmcnt(4)
	ml_byte_permute_b32 v97, v97, v100, s70
	.loc	1 347 16                        ; biv150_konly_encoded_q32.py:347:16
	ml_slb_load_b32x1  v117, v55, s85, #0, null
	.loc	1 402 12                        ; biv150_konly_encoded_q32.py:402:12
	sl_wait lmcnt(4)
	ml_byte_permute_b32 v98, v98, v97, s71
	.loc	1 347 16                        ; biv150_konly_encoded_q32.py:347:16
	ml_slb_load_b32x1  v97, v55, s89, #0, null
	.loc	1 402 12                        ; biv150_konly_encoded_q32.py:402:12
	sl_wait lmcnt(4)
	ml_matrix_mad_i32_i8_m16n16k32 v[84:87], v[98:99], v[110:111], v[84:87]
	sl_wait lmcnt(2)
	ml_matrix_mad_i32_i8_m16n16k32 v[88:91], v[98:99], v[113:114], v[88:91]
	sl_wait lmcnt(1)
	ml_matrix_mad_i32_i8_m16n16k32 v[92:95], v[98:99], v[116:117], v[92:95]
	sl_wait lmcnt(0)
	ml_matrix_mad_i32_i8_m16n16k32 v[80:83], v[98:99], v[96:97], v[80:83]
.Ltmp275:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	ml_mov_b32 v96, s68
	ml_cmp_eq_u32 tcr, s59, v96
.Ltmp276:
	.loc	1 403 46                        ; biv150_konly_encoded_q32.py:403:46
	ml_cvt_f32_i32  v80, v80
	ml_cvt_f32_i32  v81, v81
.Ltmp277:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_mov_b64 s[12:13], tcr
	ml_cmp_lt_i32 tcr, s59, v96
	sl_and_b64 {s[0:1], wcr}, s[12:13], s[8:9]
.Ltmp278:
	.loc	1 403 46                        ; biv150_konly_encoded_q32.py:403:46
	ml_cvt_f32_i32  v82, v82
	ml_cvt_f32_i32  v83, v83
.Ltmp279:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_or_b64 {s[12:13], wcr}, s[0:1], tcr
	ml_cmp_ge_u32 tcr, s6, v75
	ml_mov_b32 v75, s67
.Ltmp280:
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	ml_mul_f32 v80, v41, v80
	ml_mul_f32 v81, v42, v81
.Ltmp281:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_mov_b64 s[8:9], tcr
	ml_cmp_eq_u32 tcr, s59, v75
.Ltmp282:
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	ml_mul_f32 v82, v44, v82
	ml_mul_f32 v83, v47, v83
	.loc	1 404 48                        ; biv150_konly_encoded_q32.py:404:48
	sl_wait vmcnt(0)
	ml_mul_f32 v80, v78, v80
.Ltmp283:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_and_b64 {s[0:1], wcr}, tcr, s[8:9]
	ml_cmp_lt_i32 tcr, s59, v75
	ml_mov_b32 v75, s59
.Ltmp284:
	.loc	1 404 48                        ; biv150_konly_encoded_q32.py:404:48
	ml_mul_f32 v81, v78, v81
	ml_mul_f32 v82, v78, v82
.Ltmp285:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_or_b64 {s[16:17], wcr}, s[0:1], tcr
	ml_cmp_ge_u32 tcr, s18, v74
.Ltmp286:
	.loc	1 404 48                        ; biv150_konly_encoded_q32.py:404:48
	ml_mul_f32 v78, v78, v83
	.loc	1 405 13                        ; biv150_konly_encoded_q32.py:405:13
	ml_fma_f32 v80, s86, v80, 0
	ml_fma_f32 v81, s86, v81, 0
.Ltmp287:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_mov_b64 s[8:9], tcr
	ml_cmp_eq_u32 tcr, s68, v75
.Ltmp288:
	.loc	1 405 13                        ; biv150_konly_encoded_q32.py:405:13
	ml_fma_f32 v82, s86, v82, 0
	ml_fma_f32 v78, s86, v78, 0
.Ltmp289:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_and_b64 {s[0:1], wcr}, tcr, s[8:9]
	ml_cmp_gt_i32 tcr, s68, v75
	sl_or_b64 {s[20:21], wcr}, s[0:1], tcr
	ml_cmp_ge_u32 tcr, s6, v74
	ml_mov_b32 v74, s59
	sl_mov_b64 s[8:9], tcr
	ml_cmp_eq_u32 tcr, s67, v75
	sl_and_b64 {s[0:1], wcr}, tcr, s[8:9]
	ml_cmp_gt_i32 tcr, s67, v75
.Ltmp290:
	.loc	1 403 46                        ; biv150_konly_encoded_q32.py:403:46
	ml_cvt_f32_i32  v75, v87
	ml_cvt_f32_i32  v87, v91
	ml_cvt_f32_i32  v91, v95
.Ltmp291:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_or_b64 {s[22:23], wcr}, s[0:1], tcr
	ml_cmp_ge_u32 tcr, s18, v73
.Ltmp292:
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	ml_mul_f32 v75, v47, v75
	ml_mul_f32 v87, v47, v87
	ml_mul_f32 v91, v47, v91
.Ltmp293:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_mov_b64 s[8:9], tcr
	ml_cmp_eq_u32 tcr, s68, v74
.Ltmp294:
	.loc	1 404 48                        ; biv150_konly_encoded_q32.py:404:48
	ml_mul_f32 v75, v76, v75
	.loc	1 405 13                        ; biv150_konly_encoded_q32.py:405:13
	ml_fma_f32 v75, s86, v75, 0
.Ltmp295:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_and_b64 {s[0:1], wcr}, tcr, s[8:9]
	ml_cmp_gt_i32 tcr, s68, v74
	sl_or_b64 {s[24:25], wcr}, s[0:1], tcr
	ml_cmp_ge_u32 tcr, s6, v73
	ml_mov_b32 v73, s59
	sl_mov_b64 s[8:9], tcr
	ml_cmp_eq_u32 tcr, s67, v74
	sl_and_b64 {s[0:1], wcr}, tcr, s[8:9]
	ml_cmp_gt_i32 tcr, s67, v74
.Ltmp296:
	.loc	1 403 46                        ; biv150_konly_encoded_q32.py:403:46
	ml_cvt_f32_i32  v74, v86
	ml_cvt_f32_i32  v86, v90
	ml_cvt_f32_i32  v90, v94
.Ltmp297:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_or_b64 {s[26:27], wcr}, s[0:1], tcr
	ml_cmp_ge_u32 tcr, s18, v72
.Ltmp298:
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	ml_mul_f32 v74, v44, v74
	ml_mul_f32 v86, v44, v86
	ml_mul_f32 v90, v44, v90
.Ltmp299:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_mov_b64 s[8:9], tcr
	ml_cmp_eq_u32 tcr, s68, v73
.Ltmp300:
	.loc	1 404 48                        ; biv150_konly_encoded_q32.py:404:48
	ml_mul_f32 v74, v76, v74
	.loc	1 405 13                        ; biv150_konly_encoded_q32.py:405:13
	ml_fma_f32 v74, s86, v74, 0
.Ltmp301:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_and_b64 {s[0:1], wcr}, tcr, s[8:9]
	ml_cmp_gt_i32 tcr, s68, v73
	sl_or_b64 {s[28:29], wcr}, s[0:1], tcr
	ml_cmp_ge_u32 tcr, s6, v72
.Ltmp302:
	.loc	1 403 46                        ; biv150_konly_encoded_q32.py:403:46
	ml_cvt_f32_i32  v72, v84
	ml_cvt_f32_i32  v84, v88
	ml_cvt_f32_i32  v88, v92
.Ltmp303:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_mov_b64 s[8:9], tcr
	ml_cmp_eq_u32 tcr, s67, v73
.Ltmp304:
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	ml_mul_f32 v72, v41, v72
	ml_mul_f32 v84, v41, v84
	ml_mul_f32 v88, v41, v88
.Ltmp305:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_and_b64 {s[0:1], wcr}, tcr, s[8:9]
	ml_cmp_gt_i32 tcr, s67, v73
.Ltmp306:
	.loc	1 403 46                        ; biv150_konly_encoded_q32.py:403:46
	ml_cvt_f32_i32  v73, v85
	ml_cvt_f32_i32  v85, v89
	ml_cvt_f32_i32  v89, v93
.Ltmp307:
	.loc	2 309 42                        ; triton_attention_helpers.py:309:42 @[ biv150_konly_encoded_q32.py:396:12 ]
	sl_or_b64 {s[0:1], wcr}, s[0:1], tcr
.Ltmp308:
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	ml_mul_f32 v73, v42, v73
	ml_mul_f32 v85, v42, v85
	ml_mul_f32 v89, v42, v89
	.loc	1 404 48                        ; biv150_konly_encoded_q32.py:404:48
	ml_mul_f32 v72, v76, v72
	ml_mul_f32 v73, v76, v73
	ml_mul_f32 v76, v77, v84
	ml_mul_f32 v84, v77, v85
	ml_mul_f32 v85, v77, v86
	ml_mul_f32 v77, v77, v87
	ml_mul_f32 v86, v79, v88
	ml_mul_f32 v87, v79, v89
	ml_mul_f32 v88, v79, v90
	ml_mul_f32 v79, v79, v91
	.loc	1 405 13                        ; biv150_konly_encoded_q32.py:405:13
	ml_fma_f32 v72, s86, v72, 0
	ml_fma_f32 v73, s86, v73, 0
	ml_fma_f32 v76, s86, v76, 0
	ml_fma_f32 v83, s86, v84, 0
	ml_fma_f32 v84, s86, v85, 0
	ml_fma_f32 v77, s86, v77, 0
	ml_fma_f32 v85, s86, v86, 0
	ml_fma_f32 v86, s86, v87, 0
	ml_fma_f32 v87, s86, v88, 0
	ml_fma_f32 v79, s86, v79, 0
	ml_mov_v2s_b32 s8, v134, 0x12
	ml_mov_v2s_b32 s9, v134, 0x13
	.loc	1 411 60                        ; biv150_konly_encoded_q32.py:411:60
	sl_and_b64 {tcr, wcr}, s[8:9], s[12:13]
	.loc	1 411 73 is_stmt 0              ; biv150_konly_encoded_q32.py:411:73
	ml_csel_b32 v88, v72, v66, tcr
	ml_csel_b32 v89, v73, v66, tcr
	.loc	1 411 60                        ; biv150_konly_encoded_q32.py:411:60
	sl_and_b64 {tcr, wcr}, s[2:3], s[16:17]
	.loc	1 411 73                        ; biv150_konly_encoded_q32.py:411:73
	ml_csel_b32 v90, v74, v66, tcr
	ml_csel_b32 v91, v75, v66, tcr
	.loc	1 411 60                        ; biv150_konly_encoded_q32.py:411:60
	sl_and_b64 {tcr, wcr}, s[8:9], s[20:21]
	.loc	1 411 73                        ; biv150_konly_encoded_q32.py:411:73
	ml_csel_b32 v76, v76, v66, tcr
	ml_csel_b32 v83, v83, v66, tcr
	.loc	1 411 60                        ; biv150_konly_encoded_q32.py:411:60
	sl_and_b64 {tcr, wcr}, s[2:3], s[22:23]
	.loc	1 411 73                        ; biv150_konly_encoded_q32.py:411:73
	ml_csel_b32 v84, v84, v66, tcr
	ml_csel_b32 v77, v77, v66, tcr
	.loc	1 411 60                        ; biv150_konly_encoded_q32.py:411:60
	sl_and_b64 {tcr, wcr}, s[8:9], s[24:25]
	.loc	1 411 73                        ; biv150_konly_encoded_q32.py:411:73
	ml_csel_b32 v85, v85, v66, tcr
	ml_csel_b32 v86, v86, v66, tcr
	.loc	1 411 60                        ; biv150_konly_encoded_q32.py:411:60
	sl_and_b64 {tcr, wcr}, s[2:3], s[26:27]
	.loc	1 411 73                        ; biv150_konly_encoded_q32.py:411:73
	ml_csel_b32 v87, v87, v66, tcr
	ml_csel_b32 v79, v79, v66, tcr
	.loc	1 411 60                        ; biv150_konly_encoded_q32.py:411:60
	sl_and_b64 {tcr, wcr}, s[8:9], s[28:29]
	.loc	1 411 73                        ; biv150_konly_encoded_q32.py:411:73
	ml_csel_b32 v80, v80, v66, tcr
	ml_csel_b32 v81, v81, v66, tcr
	.loc	1 411 60                        ; biv150_konly_encoded_q32.py:411:60
	sl_and_b64 {tcr, wcr}, s[2:3], s[0:1]
	.loc	1 411 73                        ; biv150_konly_encoded_q32.py:411:73
	ml_csel_b32 v82, v82, v66, tcr
	ml_csel_b32 v78, v78, v66, tcr
.Ltmp309:
	.loc	3 192 27 is_stmt 1              ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	ml_max_f32 v72, v88, v76
	ml_max_f32 v72, v72, v85
	ml_max_f32 v72, v72, v80
.Ltmp310:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v73, v72, v32
.Ltmp311:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	ml_max_f32 v74, v89, v83
	ml_max_f32 v74, v74, v86
	ml_max_f32 v74, v74, v81
.Ltmp312:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v75, v74, v32
.Ltmp313:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	ml_max_f32 v92, v90, v84
	ml_max_f32 v92, v92, v87
	ml_max_f32 v92, v92, v82
.Ltmp314:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v93, v92, v32
.Ltmp315:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	ml_max_f32 v94, v91, v77
	ml_max_f32 v94, v94, v79
	ml_max_f32 v94, v94, v78
.Ltmp316:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v95, v94, v32
.Ltmp317:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_max_f32 v72, v72, v73
.Ltmp318:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v73, v72, v33
.Ltmp319:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_max_f32 v74, v74, v75
.Ltmp320:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v75, v74, v33
.Ltmp321:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_max_f32 v92, v92, v93
.Ltmp322:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v93, v92, v33
.Ltmp323:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_max_f32 v94, v94, v95
.Ltmp324:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v95, v94, v33
.Ltmp325:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_max_f32 v72, v72, v73
.Ltmp326:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v73, v72, v34
.Ltmp327:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_max_f32 v74, v74, v75
.Ltmp328:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v75, v74, v34
.Ltmp329:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_max_f32 v92, v92, v93
.Ltmp330:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v93, v92, v34
.Ltmp331:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_max_f32 v94, v94, v95
.Ltmp332:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v95, v94, v34
.Ltmp333:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_max_f32 v72, v72, v73
.Ltmp334:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v73, v72, v35
.Ltmp335:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_max_f32 v74, v74, v75
.Ltmp336:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v75, v74, v35
.Ltmp337:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_max_f32 v92, v92, v93
.Ltmp338:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v93, v92, v35
.Ltmp339:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_max_f32 v94, v94, v95
.Ltmp340:
	.loc	3 213 40                        ; standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v95, v94, v35
.Ltmp341:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_max_f32 v72, v72, v73
.Ltmp342:
	.loc	2 406 24                        ; triton_attention_helpers.py:406:24 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_max_f32 v72, v71, v72
	.loc	2 409 25                        ; triton_attention_helpers.py:409:25 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_cmp_ne_f32 tcr, v72, 0xff800000
	.loc	2 409 45 is_stmt 0              ; triton_attention_helpers.py:409:45 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_csel_b32 v72, v72, v65, tcr
.Ltmp343:
	.loc	3 192 27 is_stmt 1              ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(2)
	ml_max_f32 v73, v74, v75
.Ltmp344:
	.loc	2 406 24                        ; triton_attention_helpers.py:406:24 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_max_f32 v73, v70, v73
	.loc	2 409 25                        ; triton_attention_helpers.py:409:25 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_cmp_ne_f32 tcr, v73, 0xff800000
	.loc	2 409 45 is_stmt 0              ; triton_attention_helpers.py:409:45 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_csel_b32 v73, v73, v65, tcr
.Ltmp345:
	.loc	3 192 27 is_stmt 1              ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(1)
	ml_max_f32 v74, v92, v93
.Ltmp346:
	.loc	2 406 24                        ; triton_attention_helpers.py:406:24 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_max_f32 v74, v69, v74
	.loc	2 409 25                        ; triton_attention_helpers.py:409:25 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_cmp_ne_f32 tcr, v74, 0xff800000
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v88, v88, v72
.Ltmp347:
	.loc	3 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ triton_attention_helpers.py:406:31 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v75, v94, v95
.Ltmp348:
	.loc	2 406 24                        ; triton_attention_helpers.py:406:24 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_max_f32 v75, v68, v75
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v88, v88, 0x3fb8aa3b
	.loc	2 409 45                        ; triton_attention_helpers.py:409:45 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_csel_b32 v74, v74, v65, tcr
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v88, v88
	.loc	2 411 19 is_stmt 0              ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v89, v89, v73
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v89, v89, 0x3fb8aa3b
	.loc	2 409 25 is_stmt 1              ; triton_attention_helpers.py:409:25 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_cmp_ne_f32 tcr, v75, 0xff800000
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v89, v89
	.loc	2 411 19 is_stmt 0              ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v90, v90, v74
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v90, v90, 0x3fb8aa3b
	.loc	2 409 45 is_stmt 1              ; triton_attention_helpers.py:409:45 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_csel_b32 v75, v75, v65, tcr
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v90, v90
	.loc	2 411 19 is_stmt 0              ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v91, v91, v75
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v91, v91, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v76, v76, v72
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v91, v91
	ml_mul_f32 v76, v76, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v83, v83, v73
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v83, v83, 0x3fb8aa3b
	ml_exp_f32 v76, v76
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v84, v84, v74
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v84, v84, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v77, v77, v75
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v83, v83
	ml_mul_f32 v77, v77, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v85, v85, v72
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v85, v85, 0x3fb8aa3b
	ml_exp_f32 v84, v84
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v86, v86, v73
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v86, v86, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v87, v87, v74
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v77, v77
	ml_mul_f32 v87, v87, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v79, v79, v75
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v79, v79, 0x3fb8aa3b
	ml_exp_f32 v85, v85
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v80, v80, v72
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v80, v80, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v81, v81, v73
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v86, v86
	ml_mul_f32 v81, v81, 0x3fb8aa3b
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v82, v82, v74
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v82, v82, 0x3fb8aa3b
	ml_exp_f32 v87, v87
	.loc	2 411 19                        ; triton_attention_helpers.py:411:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v78, v78, v75
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v78, v78, 0x3fb8aa3b
	.loc	2 415 23 is_stmt 1              ; triton_attention_helpers.py:415:23 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v71, v71, v72
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v79, v79
	.loc	2 415 19                        ; triton_attention_helpers.py:415:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v71, v71, 0x3fb8aa3b
.Ltmp349:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	ml_add_f32 v92, v88, v76
	ml_add_f32 v92, v85, v92
.Ltmp350:
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v80, v80
	.loc	2 415 23                        ; triton_attention_helpers.py:415:23 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v70, v70, v73
	.loc	2 415 19 is_stmt 0              ; triton_attention_helpers.py:415:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v70, v70, 0x3fb8aa3b
	.loc	2 415 23                        ; triton_attention_helpers.py:415:23 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v69, v69, v74
	.loc	2 411 15 is_stmt 1              ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v81, v81
	.loc	2 415 19                        ; triton_attention_helpers.py:415:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v69, v69, 0x3fb8aa3b
.Ltmp351:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	ml_add_f32 v92, v80, v92
.Ltmp352:
	.loc	2 415 23                        ; triton_attention_helpers.py:415:23 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_sub_f32 v68, v68, v75
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v82, v82
	.loc	2 415 19                        ; triton_attention_helpers.py:415:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_mul_f32 v68, v68, 0x3fb8aa3b
.Ltmp353:
	.loc	1 447 31                        ; biv150_konly_encoded_q32.py:447:31
	ml_cvt_bf16_f32  v76, v76
	ml_cvt_bf16_f32  v80, v80
.Ltmp354:
	.loc	2 411 15                        ; triton_attention_helpers.py:411:15 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v78, v78
	.loc	2 415 19                        ; triton_attention_helpers.py:415:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v71, v71
	ml_exp_f32 v70, v70
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_fma_f32 v45, v45, v71, v92
.Ltmp355:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	ml_add_f32 v92, v89, v83
	ml_add_f32 v92, v86, v92
	ml_add_f32 v92, v81, v92
.Ltmp356:
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_fma_f32 v46, v46, v70, v92
.Ltmp357:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	ml_add_f32 v92, v90, v84
.Ltmp358:
	.loc	2 415 19                        ; triton_attention_helpers.py:415:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v69, v69
.Ltmp359:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	ml_add_f32 v92, v87, v92
	ml_add_f32 v92, v82, v92
.Ltmp360:
	.loc	1 425 20                        ; biv150_konly_encoded_q32.py:425:20
	ml_mul_f32 v28, v28, v71
.Ltmp361:
	.loc	2 415 19                        ; triton_attention_helpers.py:415:19 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_exp_f32 v68, v68
.Ltmp362:
	.loc	1 425 20                        ; biv150_konly_encoded_q32.py:425:20
	ml_mul_f32 v24, v24, v71
.Ltmp363:
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_fma_f32 v39, v39, v69, v92
.Ltmp364:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	ml_add_f32 v92, v91, v77
	ml_add_f32 v92, v79, v92
	ml_add_f32 v92, v78, v92
.Ltmp365:
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_fma_f32 v40, v40, v68, v92
.Ltmp366:
	.loc	1 425 20                        ; biv150_konly_encoded_q32.py:425:20
	ml_mul_f32 v20, v20, v71
	ml_mul_f32 v16, v16, v71
	ml_mul_f32 v12, v12, v71
	ml_mul_f32 v8, v8, v71
	ml_mul_f32 v4, v4, v71
	ml_mul_f32 v0, v0, v71
	ml_mul_f32 v29, v29, v70
	ml_mul_f32 v25, v25, v70
	ml_mul_f32 v21, v21, v70
	ml_mul_f32 v17, v17, v70
	ml_mul_f32 v13, v13, v70
	ml_mul_f32 v9, v9, v70
	ml_mul_f32 v5, v5, v70
	ml_mul_f32 v1, v1, v70
	.loc	1 447 31                        ; biv150_konly_encoded_q32.py:447:31
	ml_cvt_bf16_f32  v70, v88
	ml_cvt_bf16_f32  v71, v89
	ml_byte_permute_b32 v70, v71, v70, s76
	ml_cvt_bf16_f32  v71, v90
	ml_cvt_bf16_f32  v88, v91
	ml_byte_permute_b32 v71, v88, v71, s76
	ml_cvt_bf16_f32  v83, v83
	ml_byte_permute_b32 v76, v83, v76, s76
	ml_cvt_bf16_f32  v83, v84
	ml_cvt_bf16_f32  v77, v77
	ml_byte_permute_b32 v77, v77, v83, s76
	ml_cvt_bf16_f32  v83, v85
	ml_cvt_bf16_f32  v84, v86
	ml_byte_permute_b32 v83, v84, v83, s76
	ml_cvt_bf16_f32  v84, v87
	ml_cvt_bf16_f32  v79, v79
	ml_cvt_bf16_f32  v81, v81
	ml_cvt_bf16_f32  v82, v82
	ml_cvt_bf16_f32  v78, v78
	ml_byte_permute_b32 v79, v79, v84, s76
	ml_byte_permute_b32 v80, v81, v80, s76
	ml_byte_permute_b32 v78, v78, v82, s76
	ml_byte_permute_b32 v81, v56, v56, s77
	ml_pk_shl_b16 v81, v81, 0x40004
	ml_pk_srl_b8 v81, v81, 0x40004
	ml_byte_permute_b32 v82, v70, v71, v81
	ml_byte_permute_b32 v84, v57, v57, s77
	ml_pk_shl_b16 v84, v84, 0x40004
	ml_pk_srl_b8 v84, v84, 0x40004
	ml_byte_permute_b32 v70, v70, v71, v84
	ml_byte_permute_b32 v71, v76, v77, v81
	ml_slb_shuffle_rtn_b32 v82, v82, v60
	ml_byte_permute_b32 v76, v76, v77, v84
	ml_byte_permute_b32 v77, v83, v79, v81
	ml_byte_permute_b32 v79, v83, v79, v84
	ml_slb_shuffle_rtn_b32 v70, v70, v61
	.loc	1 425 20                        ; biv150_konly_encoded_q32.py:425:20
	ml_mul_f32 v30, v30, v69
	ml_mul_f32 v31, v31, v68
	ml_mul_f32 v26, v26, v69
	.loc	1 447 31                        ; biv150_konly_encoded_q32.py:447:31
	ml_slb_shuffle_rtn_b32 v71, v71, v60
	.loc	1 425 20                        ; biv150_konly_encoded_q32.py:425:20
	ml_mul_f32 v27, v27, v68
	ml_mul_f32 v22, v22, v69
	ml_mul_f32 v23, v23, v68
	.loc	1 447 31                        ; biv150_konly_encoded_q32.py:447:31
	ml_slb_shuffle_rtn_b32 v76, v76, v61
	.loc	1 425 20                        ; biv150_konly_encoded_q32.py:425:20
	ml_mul_f32 v18, v18, v69
	ml_mul_f32 v19, v19, v68
	ml_mul_f32 v14, v14, v69
	.loc	1 447 31                        ; biv150_konly_encoded_q32.py:447:31
	ml_slb_shuffle_rtn_b32 v77, v77, v60
	.loc	1 425 20                        ; biv150_konly_encoded_q32.py:425:20
	ml_mul_f32 v15, v15, v68
	ml_mul_f32 v10, v10, v69
	ml_mul_f32 v11, v11, v68
	.loc	1 447 31                        ; biv150_konly_encoded_q32.py:447:31
	ml_slb_shuffle_rtn_b32 v79, v79, v61
	.loc	1 425 20                        ; biv150_konly_encoded_q32.py:425:20
	ml_mul_f32 v6, v6, v69
	ml_mul_f32 v7, v7, v68
	.loc	1 447 31                        ; biv150_konly_encoded_q32.py:447:31
	ml_byte_permute_b32 v81, v80, v78, v81
	ml_slb_shuffle_rtn_b32 v81, v81, v60
	.loc	1 425 20                        ; biv150_konly_encoded_q32.py:425:20
	ml_mul_f32 v2, v2, v69
	ml_mul_f32 v3, v3, v68
	.loc	1 447 31                        ; biv150_konly_encoded_q32.py:447:31
	ml_byte_permute_b32 v68, v80, v78, v84
	ml_slb_shuffle_rtn_b32 v80, v68, v61
	ml_byte_permute_b32 v68, v58, v58, s77
	ml_pk_shl_b16 v68, v68, 0x40004
	ml_pk_srl_b8 v78, v68, 0x40004
	sl_wait lmcnt(6)
	ml_byte_permute_b32 v68, v82, v70, v78
	ml_byte_permute_b32 v69, v59, v59, s77
	ml_pk_shl_b16 v69, v69, 0x40004
	ml_pk_srl_b8 v83, v69, 0x40004
	ml_byte_permute_b32 v69, v82, v70, v83
	sl_wait lmcnt(4)
	ml_byte_permute_b32 v70, v71, v76, v78
	ml_byte_permute_b32 v71, v71, v76, v83
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v76, v77, v79, v78
	ml_byte_permute_b32 v77, v77, v79, v83
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v78, v81, v80, v78
	ml_byte_permute_b32 v79, v81, v80, v83
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	sl_barrier 
	.loc	1 403 60                        ; biv150_konly_encoded_q32.py:403:60
	sl_mov_b32 s0, 0x8000
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v80, noreg, s0, #0, null
	.loc	1 285 28                        ; biv150_konly_encoded_q32.py:285:28
	sl_add_i64 s[52:53], s[52:53], 0x1
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v81, noreg, s0, #256, null
	ml_slb_load_b32x1  v82, v62, s0, #512, null
	ml_slb_load_b32x1  v83, v62, s0, #768, null
	.loc	1 285 28                        ; biv150_konly_encoded_q32.py:285:28
	ml_mov_v2s_b32 s0, v133, 0x5
	ml_mov_v2s_b32 s1, v133, 0x6
	sl_xor_b64 {s[0:1], wcr}, s[52:53], s[0:1]
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[68:69], v[80:81], v[28:31]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v80, noreg, s94, #0, null
	ml_slb_blkload_x1  v81, noreg, s94, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[68:69], v[82:83], v[24:27]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v82, v62, s94, #512, null
	ml_slb_load_b32x1  v83, v62, s94, #768, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[68:69], v[80:81], v[20:23]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v80, noreg, s46, #0, null
	ml_slb_blkload_x1  v81, noreg, s46, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[68:69], v[82:83], v[16:19]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v82, v62, s46, #512, null
	ml_slb_load_b32x1  v83, v62, s46, #768, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[68:69], v[80:81], v[12:15]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v80, noreg, s48, #0, null
	ml_slb_blkload_x1  v81, noreg, s48, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[68:69], v[82:83], v[8:11]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v82, v62, s48, #512, null
	ml_slb_load_b32x1  v83, v62, s48, #768, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[68:69], v[80:81], v[4:7]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v80, noreg, s91, #0, null
	ml_slb_blkload_x1  v81, noreg, s91, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[68:69], v[82:83], v[0:3]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v68, v62, s91, #512, null
	ml_slb_load_b32x1  v69, v62, s91, #768, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[70:71], v[80:81], v[28:31]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v80, noreg, s4, #0, null
	ml_slb_blkload_x1  v81, noreg, s4, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[70:71], v[68:69], v[24:27]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v68, v62, s4, #512, null
	ml_slb_load_b32x1  v69, v62, s4, #768, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[70:71], v[80:81], v[20:23]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v80, noreg, s47, #0, null
	ml_slb_blkload_x1  v81, noreg, s47, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[70:71], v[68:69], v[16:19]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v68, v62, s47, #512, null
	ml_slb_load_b32x1  v69, v62, s47, #768, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[70:71], v[80:81], v[12:15]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v80, noreg, s49, #0, null
	ml_slb_blkload_x1  v81, noreg, s49, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[70:71], v[68:69], v[8:11]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v68, v62, s49, #512, null
	ml_slb_load_b32x1  v69, v62, s49, #768, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[70:71], v[80:81], v[4:7]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v80, noreg, s92, #0, null
	ml_slb_blkload_x1  v81, noreg, s92, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[70:71], v[68:69], v[0:3]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v68, v62, s92, #512, null
	ml_slb_load_b32x1  v69, v62, s92, #768, null
	ml_slb_blkload_x1  v70, noreg, s5, #0, null
	ml_slb_blkload_x1  v71, noreg, s5, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(4)
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[76:77], v[80:81], v[28:31]
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[76:77], v[68:69], v[24:27]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v68, v62, s5, #512, null
	ml_slb_load_b32x1  v69, v62, s5, #768, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[76:77], v[70:71], v[20:23]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v70, noreg, s69, #0, null
	ml_slb_blkload_x1  v71, noreg, s69, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[76:77], v[68:69], v[16:19]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v68, v62, s69, #512, null
	ml_slb_load_b32x1  v69, v62, s69, #768, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[76:77], v[70:71], v[12:15]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v70, noreg, s54, #0, null
	ml_slb_blkload_x1  v71, noreg, s54, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[76:77], v[68:69], v[8:11]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v68, v62, s54, #512, null
	ml_slb_load_b32x1  v69, v62, s54, #768, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[76:77], v[70:71], v[4:7]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v70, noreg, s93, #0, null
	ml_slb_blkload_x1  v71, noreg, s93, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[76:77], v[68:69], v[0:3]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v68, v62, s93, #512, null
	ml_slb_load_b32x1  v69, v62, s93, #768, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[28:31], v[78:79], v[70:71], v[28:31]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v70, noreg, s87, #0, null
	ml_slb_blkload_x1  v71, noreg, s87, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[24:27], v[78:79], v[68:69], v[24:27]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v68, v62, s87, #512, null
	ml_slb_load_b32x1  v69, v62, s87, #768, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[20:23], v[78:79], v[70:71], v[20:23]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v70, noreg, s7, #0, null
	ml_slb_blkload_x1  v71, noreg, s7, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[16:19], v[78:79], v[68:69], v[16:19]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v68, v62, s7, #512, null
	ml_slb_load_b32x1  v69, v62, s7, #768, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[12:15], v[78:79], v[70:71], v[12:15]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_blkload_x1  v70, noreg, s55, #0, null
	ml_slb_blkload_x1  v71, noreg, s55, #256, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[8:11], v[78:79], v[68:69], v[8:11]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_load_b32x1  v68, v62, s55, #512, null
	ml_slb_load_b32x1  v69, v62, s55, #768, null
	.loc	1 447 41                        ; biv150_konly_encoded_q32.py:447:41
	sl_wait lmcnt(2)
	ml_matrix_mad_f32_bf16_m16n16k16 v[4:7], v[78:79], v[70:71], v[4:7]
	ml_mov_b32 v71, v72
	ml_mov_b32 v70, v73
	sl_wait lmcnt(0)
	ml_matrix_mad_f32_bf16_m16n16k16 v[0:3], v[78:79], v[68:69], v[0:3]
	ml_mov_b32 v69, v74
	ml_mov_b32 v68, v75
	.loc	1 285 28                        ; biv150_konly_encoded_q32.py:285:28
	sl_cbr_wcrz BB0_60, wcr
BB0_39:                                 ; =>This Inner Loop Header: Depth=1
	.loc	1 0 28 is_stmt 0                ; biv150_konly_encoded_q32.py:0:28
	sl_mov_b32 s45, s33
	.loc	1 286 25 is_stmt 1              ; biv150_konly_encoded_q32.py:286:25
	sl_shl_b64 {s[58:59], wcr}, s[52:53], 0x6
	.loc	1 286 37 is_stmt 0              ; biv150_konly_encoded_q32.py:286:37
	ml_mov_v2s_b32 s0, v133, 0x9
	ml_mov_v2s_b32 s1, v133, 0xa
	ml_or_b32 v77, s58, v48
	ml_add_i32 v76, v77, 0x20
	ml_or_b32 v75, s58, v37
	sl_or_b64 {s[64:65], wcr}, s[58:59], s[0:1]
	ml_mov_v2s_b32 s0, v133, 0xb
	ml_mov_v2s_b32 s1, v133, 0xc
	ml_add_i32 v74, v75, 0x10
	ml_add_i32 v73, v75, 0x20
	ml_add_i32 v72, v75, 0x30
	sl_or_b64 {s[62:63], wcr}, s[58:59], s[0:1]
	ml_mov_v2s_b32 s0, v133, 0xd
	ml_mov_v2s_b32 s1, v133, 0xe
	.loc	1 287 33 is_stmt 1              ; biv150_konly_encoded_q32.py:287:33
	ml_cmp_gt_u32 tcr, s40, v77
	.loc	1 286 37                        ; biv150_konly_encoded_q32.py:286:37
	ml_mov_v2s_b32 s2, v76, 0x0
	sl_mov_b32 s3, s59
	sl_or_b64 {s[60:61], wcr}, s[58:59], s[0:1]
	.loc	1 287 33                        ; biv150_konly_encoded_q32.py:287:33
	sl_cmp_eq_u32 wcr, s59, 0x0
	sl_sub_bi_u64 s[0:1], s[10:11], s[10:11], wcr
	sl_and_b64 {s[8:9], wcr}, s[0:1], tcr
	sl_cmp_lt_i32 wcr, s59, 0x0
	sl_sub_bi_u64 s[16:17], s[10:11], s[10:11], wcr
	.loc	1 286 37                        ; biv150_konly_encoded_q32.py:286:37
	ml_mov_v2s_b32 s0, v77, 0x0
	sl_mov_b32 s1, s59
	.loc	1 290 52                        ; biv150_konly_encoded_q32.py:290:52
	sl_srl_b64 {s[12:13], wcr}, s[58:59], 0x2
	sl_add_i64 s[12:13], s[42:43], s[12:13]
	sl_srl_b64 {s[20:21], wcr}, s[64:65], 0x2
	ml_mov_v2s_b32 s22, v133, 0x12
	ml_mov_v2s_b32 s23, v133, 0x13
	sl_srl_b64 {s[24:25], wcr}, s[62:63], 0x2
	sl_and_b64 {s[24:25], wcr}, s[24:25], s[56:57]
	sl_add_i64 s[24:25], s[42:43], s[24:25]
	sl_and_b64 {s[20:21], wcr}, s[20:21], s[22:23]
	sl_add_i64 s[20:21], s[42:43], s[20:21]
	sl_mov_b64 s[22:23], s[14:15]
	sl_mov_b64 s[26:27], s[14:15]
	sl_srl_b64 {s[28:29], wcr}, s[60:61], 0x2
	sl_and_b64 {s[28:29], wcr}, s[28:29], s[56:57]
	sl_add_i64 s[28:29], s[42:43], s[28:29]
	sl_mov_b64 s[30:31], s[14:15]
	sl_srl_b64 {s[0:1], wcr}, s[0:1], 0x2
	sl_and_b64 {s[0:1], wcr}, s[0:1], s[56:57]
	sl_add_i64 s[32:33], s[42:43], s[0:1]
	sl_mov_b64 s[34:35], s[14:15]
	sl_srl_b64 {s[0:1], wcr}, s[2:3], 0x2
	sl_and_b64 {s[0:1], wcr}, s[0:1], s[56:57]
	sl_add_i64 s[36:37], s[42:43], s[0:1]
	ml_mov_b32 v77, s59
	.loc	1 290 12 is_stmt 0              ; biv150_konly_encoded_q32.py:290:12
	ml_lsa_load_dword v84, s[12:15], noreg, noreg, #0, ca
	.loc	1 290 52                        ; biv150_konly_encoded_q32.py:290:52
	ml_srl_b32 v78, v77, 0x2
	ml_srl_b32 v79, v74, 0x2
	ml_shl_b32 v77, v77, 0x1e
	.loc	1 290 12                        ; biv150_konly_encoded_q32.py:290:12
	ml_lsa_load_dword v85, s[20:23], noreg, noreg, #0, ca
	.loc	1 290 52                        ; biv150_konly_encoded_q32.py:290:52
	ml_anyop3_b32 v77, v79, v77, -12, 0xe0
	ml_addo_u32 {v77, tcr}, s42, v77
	ml_and_b32 v78, v78, 0x3fffffff
	.loc	1 290 12                        ; biv150_konly_encoded_q32.py:290:12
	ml_lsa_load_dword v86, s[24:27], noreg, noreg, #0, ca
	.loc	1 290 52                        ; biv150_konly_encoded_q32.py:290:52
	ml_mov_b32 v83, s43
	ml_addc_i32 v78, v83, v78, tcr
	ml_mov_b32 v80, s59
	.loc	1 290 12                        ; biv150_konly_encoded_q32.py:290:12
	ml_lsa_load_dword v87, s[28:31], noreg, noreg, #0, ca
	.loc	1 290 52                        ; biv150_konly_encoded_q32.py:290:52
	ml_srl_b32 v79, v73, 0x2
	ml_shl_b32 v81, v80, 0x1e
	ml_anyop3_b32 v79, v79, v81, -8, 0xe0
	.loc	1 290 12                        ; biv150_konly_encoded_q32.py:290:12
	ml_lsa_load_dword v88, s[32:35], noreg, noreg, #0, ca
	.loc	1 290 52                        ; biv150_konly_encoded_q32.py:290:52
	ml_addo_u32 {v79, tcr}, s42, v79
	sl_mov_b64 s[38:39], s[14:15]
	ml_srl_b32 v80, v80, 0x2
	.loc	1 290 12                        ; biv150_konly_encoded_q32.py:290:12
	ml_lsa_load_dword v89, s[36:39], noreg, noreg, #0, ca
	.loc	1 290 52                        ; biv150_konly_encoded_q32.py:290:52
	ml_addc_i32 v80, v83, v80, tcr
	ml_mov_b32 v90, s59
	ml_srl_b32 v81, v72, 0x2
	.loc	1 290 12                        ; biv150_konly_encoded_q32.py:290:12
	ml_lsa_load_a64_dword  v78, v[77:78], kop=0
	.loc	1 290 52                        ; biv150_konly_encoded_q32.py:290:52
	ml_shl_b32 v77, v90, 0x1e
	ml_anyop3_b32 v77, v81, v77, -4, 0xe0
	ml_addo_u32 {v82, tcr}, s42, v77
	.loc	1 290 12                        ; biv150_konly_encoded_q32.py:290:12
	ml_lsa_load_a64_dword  v81, v[79:80], kop=0
	.loc	1 290 52                        ; biv150_konly_encoded_q32.py:290:52
	ml_srl_b32 v77, v90, 0x2
	ml_and_b32 v77, v77, 0x3fffffff
	ml_addc_i32 v83, v83, v77, tcr
	.loc	1 290 12                        ; biv150_konly_encoded_q32.py:290:12
	ml_lsa_load_a64_dword  v80, v[82:83], kop=0
	.loc	1 287 33 is_stmt 1              ; biv150_konly_encoded_q32.py:287:33
	sl_or_b64 {s[0:1], wcr}, s[8:9], s[16:17]
	.loc	1 290 12                        ; biv150_konly_encoded_q32.py:290:12
	sl_wait vmcnt(8)
	ml_mov_v2s_b32 s12, v84, 0x0
	sl_wait vmcnt(7)
	ml_mov_v2s_b32 s24, v85, 0x0
	sl_wait vmcnt(6)
	ml_mov_v2s_b32 s22, v86, 0x0
	sl_wait vmcnt(5)
	ml_mov_v2s_b32 s20, v87, 0x0
	sl_wait vmcnt(4)
	ml_mov_v2s_b32 s16, v88, 0x0
	ml_mov_b32 v77, 0x0
	sl_wait vmcnt(3)
	ml_mov_v2s_b32 s26, v89, 0x0
	.loc	1 347 16                        ; biv150_konly_encoded_q32.py:347:16
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	; mask branch BB0_41
	sl_cbr_tmskaz BB0_41
BB0_40:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 291 13                        ; biv150_konly_encoded_q32.py:291:13
	sl_sra_b32 {s17, wcr}, s16, 0x1f
	.loc	1 340 46                        ; biv150_konly_encoded_q32.py:340:46
	sl_shl_b64 {s[0:1], wcr}, s[16:17], 0xe
	.loc	1 347 16                        ; biv150_konly_encoded_q32.py:347:16
	ml_mov_v2s_b32 s2, v133, 0xf
	ml_mov_v2s_b32 s3, v133, 0x10
	sl_add_i64 s[16:17], s[2:3], s[0:1]
	ml_lsa_load_dword v77, s[16:19], unsigned v64, noreg, #0, ca|mie
BB0_41:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 0 16 is_stmt 0                ; biv150_konly_encoded_q32.py:0:16
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 287 33 is_stmt 1              ; biv150_konly_encoded_q32.py:287:33
	ml_cmp_gt_u32 tcr, s40, v76
	ml_mov_b32 v76, 0x0
	ml_mov_b32 v79, s59
	sl_mov_b64 s[8:9], tcr
	ml_cmp_eq_u32 tcr, v79, 0x0
	sl_and_b64 {s[0:1], wcr}, tcr, s[8:9]
	ml_cmp_lt_i32 tcr, v79, 0x0
	ml_mov_b32 v79, 0x0
	sl_or_b64 {s[0:1], wcr}, s[0:1], tcr
	.loc	1 347 16                        ; biv150_konly_encoded_q32.py:347:16
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	; mask branch BB0_43
	sl_cbr_tmskaz BB0_43
BB0_42:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 0 0 is_stmt 0                 ; biv150_konly_encoded_q32.py:0
	sl_sra_b32 {s27, wcr}, s26, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[26:27], 0xe
	.loc	1 347 16                        ; biv150_konly_encoded_q32.py:347:16
	ml_mov_v2s_b32 s2, v133, 0xf
	ml_mov_v2s_b32 s3, v133, 0x10
	sl_add_i64 s[16:17], s[2:3], s[0:1]
	ml_lsa_load_dword v79, s[16:19], unsigned v64, noreg, #0, ca|mie
BB0_43:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 0 16                          ; biv150_konly_encoded_q32.py:0:16
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 286 37 is_stmt 1              ; biv150_konly_encoded_q32.py:286:37
	ml_mov_v2s_b32 s0, v133, 0x7
	ml_mov_v2s_b32 s1, v133, 0x8
	.loc	1 347 16                        ; biv150_konly_encoded_q32.py:347:16
	sl_wait vmcnt(0)
	ml_slb_store_b32x1  v77, v49, s80, #0, null
	ml_mov_b32 v77, 0x0
	sl_mov_b32 s33, s45
	.loc	1 286 37                        ; biv150_konly_encoded_q32.py:286:37
	sl_or_b64 {s[0:1], wcr}, s[58:59], s[0:1]
	.loc	1 287 33                        ; biv150_konly_encoded_q32.py:287:33
	sl_min_i64 s[0:1], s[0:1], s[40:41]
	sl_xor_b64 {s[0:1], wcr}, s[0:1], s[40:41]
	.loc	1 347 16                        ; biv150_konly_encoded_q32.py:347:16
	ml_slb_store_b32x1  v79, v49, s81, #0, null
	sl_mov_b32 s3, 0x1000
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	sl_cbr_wcrz BB0_45, wcr
; %bb.44:                               ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 291 13                        ; biv150_konly_encoded_q32.py:291:13
	sl_sra_b32 {s13, wcr}, s12, 0x1f
	.loc	1 353 34                        ; biv150_konly_encoded_q32.py:353:34
	sl_shl_b64 {s[0:1], wcr}, s[12:13], 0xe
	.loc	1 353 16 is_stmt 0              ; biv150_konly_encoded_q32.py:353:16
	sl_add_i64 s[0:1], s[82:83], s[0:1]
	sl_add_i64 s[16:17], s[0:1], s[50:51]
	ml_lsa_blkload_x1 v77, s[16:19], noreg, noreg, #0, ca
BB0_45:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 287 33 is_stmt 1              ; biv150_konly_encoded_q32.py:287:33
	sl_min_i64 s[0:1], s[64:65], s[40:41]
	sl_xor_b64 {s[0:1], wcr}, s[0:1], s[40:41]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	sl_cbr_wcrz BB0_47, wcr
; %bb.46:                               ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 0 0 is_stmt 0                 ; biv150_konly_encoded_q32.py:0
	sl_sra_b32 {s25, wcr}, s24, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[24:25], 0xe
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	sl_add_i64 s[0:1], s[82:83], s[0:1]
	sl_add_i64 s[16:17], s[0:1], s[50:51]
	ml_lsa_blkload_x1 v76, s[16:19], noreg, noreg, #0, ca
BB0_47:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 287 33 is_stmt 1              ; biv150_konly_encoded_q32.py:287:33
	sl_min_i64 s[0:1], s[62:63], s[40:41]
	sl_xor_b64 {s[0:1], wcr}, s[0:1], s[40:41]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_mov_b32 v79, 0x0
	ml_mov_b32 v82, 0x0
	sl_cbr_wcrz BB0_49, wcr
; %bb.48:                               ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 0 0 is_stmt 0                 ; biv150_konly_encoded_q32.py:0
	sl_sra_b32 {s23, wcr}, s22, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[22:23], 0xe
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	sl_add_i64 s[0:1], s[82:83], s[0:1]
	sl_add_i64 s[16:17], s[0:1], s[50:51]
	ml_lsa_blkload_x1 v82, s[16:19], noreg, noreg, #0, ca
BB0_49:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 287 33 is_stmt 1              ; biv150_konly_encoded_q32.py:287:33
	sl_min_i64 s[0:1], s[60:61], s[40:41]
	sl_xor_b64 {s[0:1], wcr}, s[0:1], s[40:41]
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	sl_cbr_wcrz BB0_51, wcr
; %bb.50:                               ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 0 0 is_stmt 0                 ; biv150_konly_encoded_q32.py:0
	sl_sra_b32 {s21, wcr}, s20, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[20:21], 0xe
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	sl_add_i64 s[0:1], s[82:83], s[0:1]
	sl_add_i64 s[16:17], s[0:1], s[50:51]
	ml_lsa_blkload_x1 v79, s[16:19], noreg, noreg, #0, ca
BB0_51:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 287 33 is_stmt 1              ; biv150_konly_encoded_q32.py:287:33
	ml_cmp_gt_u32 tcr, s40, v75
	ml_mov_b32 v83, s59
	sl_mov_b64 s[8:9], tcr
	ml_cmp_eq_u32 tcr, v83, 0x0
	sl_and_b64 {s[0:1], wcr}, tcr, s[8:9]
	ml_cmp_lt_i32 tcr, v83, 0x0
	sl_or_b64 {s[0:1], wcr}, s[0:1], tcr
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	sl_wait vmcnt(0) lmcnt(0)
	sl_barrier 
	sl_add_i32 s2, s66, 0x8000
	ml_slb_store_b16  v77, v67, s2, #0, null
	ml_srl_b32 v77, v77, 0x10
	ml_slb_store_b16  v77, v67, s2, #4, null
	sl_add_i32 s2, s66, 0x9000
	.loc	1 360 25                        ; biv150_konly_encoded_q32.py:360:25
	ml_mov_b32 v77, 0x3f800000
	.loc	1 353 16                        ; biv150_konly_encoded_q32.py:353:16
	ml_slb_store_b16  v76, v67, s2, #0, null
	ml_srl_b32 v76, v76, 0x10
	ml_slb_store_b16  v76, v67, s2, #4, null
	sl_add_i32 s2, s66, 0xa000
	ml_srl_b32 v76, v82, 0x10
	ml_slb_store_b16  v82, v67, s2, #0, null
	ml_slb_store_b16  v76, v67, s2, #4, null
	sl_add_i32 s2, s66, 0xb000
	ml_mov_b32 v76, 0x3f800000
	ml_slb_store_b16  v79, v67, s2, #0, null
	ml_srl_b32 v79, v79, 0x10
	ml_slb_store_b16  v79, v67, s2, #4, null
.Ltmp367:
	.loc	1 30 19                         ; biv150_konly_encoded_q32.py:30:19 @[ biv150_konly_encoded_q32.py:360:25 ]
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	; mask branch BB0_53
.Ltmp368:
BB0_52:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 291 13                        ; biv150_konly_encoded_q32.py:291:13
	sl_sra_b32 {s13, wcr}, s12, 0x1f
.Ltmp369:
	.loc	1 30 25                         ; biv150_konly_encoded_q32.py:30:25 @[ biv150_konly_encoded_q32.py:360:25 ]
	sl_shl_b64 {s[0:1], wcr}, s[12:13], 0xe
	sl_add_i64 s[0:1], s[78:79], s[0:1]
	sl_mull_u32 s32, s14, 0x4
	.loc	1 30 19 is_stmt 0               ; biv150_konly_encoded_q32.py:30:19 @[ biv150_konly_encoded_q32.py:360:25 ]
	sl_add_i64 s[16:17], s[0:1], s[32:33]
	ml_lsa_load_dword v76, s[16:19], unsigned v43, s3, #0, ca|mie
.Ltmp370:
BB0_53:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 0 19                          ; biv150_konly_encoded_q32.py:0:19
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 287 33 is_stmt 1              ; biv150_konly_encoded_q32.py:287:33
	ml_cmp_gt_u32 tcr, s40, v74
	ml_mov_b32 v79, s59
	sl_mov_b64 s[8:9], tcr
	ml_cmp_eq_u32 tcr, v79, 0x0
	sl_and_b64 {s[0:1], wcr}, tcr, s[8:9]
	ml_cmp_lt_i32 tcr, v79, 0x0
	sl_or_b64 {s[0:1], wcr}, s[0:1], tcr
.Ltmp371:
	.loc	1 30 19                         ; biv150_konly_encoded_q32.py:30:19 @[ biv150_konly_encoded_q32.py:360:25 ]
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	; mask branch BB0_55
	sl_cbr_tmskaz BB0_55
.Ltmp372:
BB0_54:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 291 13                        ; biv150_konly_encoded_q32.py:291:13
	ml_sra_b32 v77, v78, 0x1f
.Ltmp373:
	.loc	1 30 25                         ; biv150_konly_encoded_q32.py:30:25 @[ biv150_konly_encoded_q32.py:360:25 ]
	ml_shl_b32 v79, v78, 0xe
	ml_shl_b32 v77, v77, 0xe
	ml_addo_u32 {v79, tcr}, s78, v79
	ml_srl_b32 v78, v78, 0x12
	ml_or_b32 v77, v77, v78
	ml_mov_b32 v78, s79
	ml_addc_i32 v77, v78, v77, tcr
	ml_addo_u32 {v78, tcr}, v63, v79
	sl_mull_u32 s0, s14, 0x4
	ml_addc_i32 v77, 0, v77, tcr
	ml_addo_u32 {v78, tcr}, s0, v78
	ml_addc_i32 v79, 0, v77, tcr
	ml_addo_u32 {v77, tcr}, s3, v78
	ml_addc_i32 v78, 0, v79, tcr
	.loc	1 30 19 is_stmt 0               ; biv150_konly_encoded_q32.py:30:19 @[ biv150_konly_encoded_q32.py:360:25 ]
	ml_lsa_load_a64_dword  v77, v[77:78], kop=0
.Ltmp374:
BB0_55:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 0 19                          ; biv150_konly_encoded_q32.py:0:19
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 287 33 is_stmt 1              ; biv150_konly_encoded_q32.py:287:33
	ml_cmp_gt_u32 tcr, s40, v73
	ml_mov_b32 v78, s59
	ml_mov_b32 v79, 0x3f800000
	sl_mov_b64 s[8:9], tcr
	ml_cmp_eq_u32 tcr, v78, 0x0
	sl_and_b64 {s[0:1], wcr}, tcr, s[8:9]
	ml_cmp_lt_i32 tcr, v78, 0x0
	.loc	1 360 25                        ; biv150_konly_encoded_q32.py:360:25
	ml_mov_b32 v78, 0x3f800000
	.loc	1 287 33                        ; biv150_konly_encoded_q32.py:287:33
	sl_or_b64 {s[0:1], wcr}, s[0:1], tcr
.Ltmp375:
	.loc	1 30 19                         ; biv150_konly_encoded_q32.py:30:19 @[ biv150_konly_encoded_q32.py:360:25 ]
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	; mask branch BB0_57
	sl_cbr_tmskaz BB0_57
.Ltmp376:
BB0_56:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 291 13                        ; biv150_konly_encoded_q32.py:291:13
	ml_sra_b32 v79, v81, 0x1f
.Ltmp377:
	.loc	1 30 25                         ; biv150_konly_encoded_q32.py:30:25 @[ biv150_konly_encoded_q32.py:360:25 ]
	ml_shl_b32 v82, v81, 0xe
	ml_shl_b32 v79, v79, 0xe
	ml_addo_u32 {v82, tcr}, s78, v82
	ml_srl_b32 v81, v81, 0x12
	ml_or_b32 v79, v79, v81
	ml_mov_b32 v81, s79
	ml_addc_i32 v79, v81, v79, tcr
	ml_addo_u32 {v81, tcr}, v63, v82
	sl_mull_u32 s0, s14, 0x4
	ml_addc_i32 v79, 0, v79, tcr
	ml_addo_u32 {v81, tcr}, s0, v81
	ml_addc_i32 v79, 0, v79, tcr
	ml_addo_u32 {v81, tcr}, s3, v81
	ml_addc_i32 v82, 0, v79, tcr
	.loc	1 30 19 is_stmt 0               ; biv150_konly_encoded_q32.py:30:19 @[ biv150_konly_encoded_q32.py:360:25 ]
	ml_lsa_load_a64_dword  v79, v[81:82], kop=0
.Ltmp378:
BB0_57:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 0 19                          ; biv150_konly_encoded_q32.py:0:19
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 287 33 is_stmt 1              ; biv150_konly_encoded_q32.py:287:33
	ml_cmp_gt_u32 tcr, s40, v72
	ml_mov_b32 v81, s59
	sl_mov_b64 s[8:9], tcr
	ml_cmp_eq_u32 tcr, v81, 0x0
	sl_and_b64 {s[0:1], wcr}, tcr, s[8:9]
	ml_cmp_lt_i32 tcr, v81, 0x0
	sl_or_b64 {s[0:1], wcr}, s[0:1], tcr
.Ltmp379:
	.loc	1 30 19                         ; biv150_konly_encoded_q32.py:30:19 @[ biv150_konly_encoded_q32.py:360:25 ]
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	; mask branch BB0_38
	sl_cbr_tmskaz BB0_38
.Ltmp380:
BB0_58:                                 ;   in Loop: Header=BB0_39 Depth=1
	.loc	1 291 13                        ; biv150_konly_encoded_q32.py:291:13
	ml_sra_b32 v78, v80, 0x1f
.Ltmp381:
	.loc	1 30 25                         ; biv150_konly_encoded_q32.py:30:25 @[ biv150_konly_encoded_q32.py:360:25 ]
	ml_shl_b32 v81, v80, 0xe
	ml_shl_b32 v78, v78, 0xe
	ml_addo_u32 {v81, tcr}, s78, v81
	ml_srl_b32 v80, v80, 0x12
	ml_or_b32 v78, v78, v80
	ml_mov_b32 v80, s79
	ml_addc_i32 v78, v80, v78, tcr
	ml_addo_u32 {v80, tcr}, v63, v81
	sl_mull_u32 s0, s14, 0x4
	ml_addc_i32 v78, 0, v78, tcr
	ml_addo_u32 {v80, tcr}, s0, v80
	ml_addc_i32 v78, 0, v78, tcr
	ml_addo_u32 {v80, tcr}, s3, v80
	ml_addc_i32 v81, 0, v78, tcr
	.loc	1 30 19 is_stmt 0               ; biv150_konly_encoded_q32.py:30:19 @[ biv150_konly_encoded_q32.py:360:25 ]
	ml_lsa_load_a64_dword  v78, v[80:81], kop=0
	sl_jump BB0_38
.Ltmp382:
BB0_59:                                 ; %.._crit_edge109_crit_edge
	.loc	1 542 16 is_stmt 1              ; biv150_konly_encoded_q32.py:542:16
	ml_shl_b32 v38, v16, 0x1
	ml_mov_b32 v0, 0x0
	ml_mov_b32 v1, 0x0
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
	ml_mov_b32 v45, 0x0
	ml_mov_b32 v46, 0x0
	ml_mov_b32 v39, 0x0
	ml_mov_b32 v40, 0x0
	ml_mov_b32 v2, 0x0
	ml_mov_b32 v3, 0x0
	ml_mov_v2s_b32 s14, v133, 0x0
	ml_mov_v2s_b32 s1, v133, 0x11
	ml_mov_v2s_b32 s75, v134, 0x11
	ml_mov_v2s_b32 s2, v134, 0x10
	.loc	1 285 28                        ; biv150_konly_encoded_q32.py:285:28
	sl_jump BB0_61
BB0_60:                                 ; %._crit_edge109.loopexit
	.loc	1 0 28 is_stmt 0                ; biv150_konly_encoded_q32.py:0:28
	ml_mov_b32 v36, v28
	ml_mov_v2s_b32 s1, v133, 0x11
	ml_mov_v2s_b32 s2, v134, 0x10
	ml_mov_v2s_b32 s98, v133, 0x1
	sl_mov_b32 tcr_lo, s98
	sl_mov_b32 s98, 0xffffffff
	ml_mov_v2s_b32 s98, v133, 0x2
	sl_mov_b32 tcr_hi, s98
	sl_mov_b32 s98, 0xffffffff
BB0_61:                                 ; %._crit_edge109
.Ltmp383:
	.loc	3 213 40 is_stmt 1              ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_xor_b32 v28, tid, 0x8
.Ltmp384:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v32, v45, v28
.Ltmp385:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_xor_b32 v34, tid, 0x4
	ml_xor_b32 v42, tid, 0x2
	ml_mov_b32 v71, 0x3276
.Ltmp386:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v33, v46, v28
.Ltmp387:
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	sl_mov_b32 s0, 0x1000504
	.loc	1 541 29                        ; biv150_konly_encoded_q32.py:541:29
	sl_mov_b32 s15, 0xfff00004
	sl_mov_b64 s[18:19], s[14:15]
.Ltmp388:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v41, v39, v28
	ml_slb_shuffle_rtn_b32 v28, v40, v28
.Ltmp389:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_add_f32 v32, v45, v32
.Ltmp390:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v35, v32, v34
.Ltmp391:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_add_f32 v33, v46, v33
.Ltmp392:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v37, v33, v34
.Ltmp393:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_add_f32 v39, v39, v41
.Ltmp394:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v41, v39, v34
.Ltmp395:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_add_f32 v28, v40, v28
.Ltmp396:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v34, v28, v34
.Ltmp397:
	.loc	3 213 40                        ; standard.py:213:40 @[ biv150_konly_encoded_q32.py:14:39 @[ biv150_konly_encoded_q32.py:238:48 ] ]
	ml_xor_b32 v40, tid, 0x1
.Ltmp398:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_add_f32 v32, v32, v35
.Ltmp399:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v35, v32, v42
.Ltmp400:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_add_f32 v33, v33, v37
.Ltmp401:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v37, v33, v42
.Ltmp402:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_add_f32 v39, v39, v41
.Ltmp403:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v41, v39, v42
.Ltmp404:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_add_f32 v28, v28, v34
.Ltmp405:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v34, v28, v42
.Ltmp406:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_add_f32 v32, v32, v35
.Ltmp407:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v35, v32, v40
.Ltmp408:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(3)
	ml_add_f32 v33, v33, v37
.Ltmp409:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v37, v33, v40
.Ltmp410:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(2)
	ml_add_f32 v28, v28, v34
	sl_wait lmcnt(1)
	ml_add_f32 v32, v32, v35
.Ltmp411:
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_add_f32 v32, v32, 0x0
.Ltmp412:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	ml_add_f32 v35, v39, v41
.Ltmp413:
	.loc	1 507 20                        ; biv150_konly_encoded_q32.py:507:20
	ml_rcp_f32 v39, v32
.Ltmp414:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(0)
	ml_add_f32 v33, v33, v37
.Ltmp415:
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_add_f32 v33, v33, 0x0
.Ltmp416:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v34, v35, v40
.Ltmp417:
	.loc	1 507 20                        ; biv150_konly_encoded_q32.py:507:20
	ml_rcp_f32 v37, v33
	ml_xor_b32 v32, v32, 0x80000000
	ml_xor_b32 v33, v33, 0x80000000
	ml_mul_f32 v42, v24, v39
	ml_mul_f32 v44, v20, v39
	ml_mul_f32 v46, v16, v39
	ml_mul_f32 v41, v29, v37
	ml_mul_f32 v43, v25, v37
	ml_mul_f32 v45, v21, v37
	ml_mul_f32 v47, v17, v37
	ml_mul_f32 v48, v12, v39
	ml_mul_f32 v49, v13, v37
	ml_fma_f32 v29, v33, v41, v29
	ml_fma_f32 v24, v32, v42, v24
	ml_fma_f32 v25, v33, v43, v25
	ml_fma_f32 v20, v32, v44, v20
	ml_fma_f32 v21, v33, v45, v21
	ml_fma_f32 v16, v32, v46, v16
	ml_fma_f32 v17, v33, v47, v17
	ml_fma_f32 v12, v32, v48, v12
.Ltmp418:
	.loc	3 315 36                        ; standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ]
	ml_slb_shuffle_rtn_b32 v40, v28, v40
.Ltmp419:
	.loc	1 507 20                        ; biv150_konly_encoded_q32.py:507:20
	ml_fma_f32 v13, v33, v49, v13
	ml_mul_f32 v50, v8, v39
	ml_fma_f32 v8, v32, v50, v8
	ml_mul_f32 v51, v9, v37
	ml_fma_f32 v9, v33, v51, v9
	ml_mul_f32 v52, v4, v39
	ml_fma_f32 v4, v32, v52, v4
.Ltmp420:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(1)
	ml_add_f32 v34, v35, v34
.Ltmp421:
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_add_f32 v34, v34, 0x0
.Ltmp422:
	.loc	1 507 20                        ; biv150_konly_encoded_q32.py:507:20
	ml_mul_f32 v35, v5, v37
	ml_rcp_f32 v53, v34
	ml_fma_f32 v5, v33, v35, v5
	ml_mul_f32 v54, v1, v37
	ml_fma_f32 v33, v33, v54, v1
	ml_xor_b32 v1, v34, 0x80000000
	ml_mul_f32 v68, v0, v39
	ml_mul_f32 v55, v30, v53
	ml_fma_f32 v30, v1, v55, v30
	ml_mul_f32 v56, v26, v53
.Ltmp423:
	.loc	3 285 15                        ; standard.py:285:15 @[ standard.py:315:36 @[ triton_attention_helpers.py:413:17 @[ biv150_konly_encoded_q32.py:424:44 ] ] ]
	sl_wait lmcnt(0)
	ml_add_f32 v28, v28, v40
.Ltmp424:
	.loc	2 417 24                        ; triton_attention_helpers.py:417:24 @[ biv150_konly_encoded_q32.py:424:44 ]
	ml_add_f32 v28, v28, 0x0
.Ltmp425:
	.loc	1 507 20                        ; biv150_konly_encoded_q32.py:507:20
	ml_fma_f32 v26, v1, v56, v26
	ml_rcp_f32 v40, v28
	ml_xor_b32 v28, v28, 0x80000000
	ml_mul_f32 v58, v22, v53
	ml_fma_f32 v22, v1, v58, v22
	ml_mul_f32 v60, v18, v53
	ml_fma_f32 v18, v1, v60, v18
	ml_mul_f32 v34, v31, v40
	ml_fma_f32 v31, v28, v34, v31
	ml_mul_f32 v57, v27, v40
	ml_fma_f32 v27, v28, v57, v27
	ml_mul_f32 v59, v23, v40
	ml_fma_f32 v23, v28, v59, v23
	ml_mul_f32 v61, v19, v40
	ml_fma_f32 v19, v28, v61, v19
	ml_mul_f32 v62, v14, v53
	ml_fma_f32 v14, v1, v62, v14
	ml_mul_f32 v63, v15, v40
	ml_fma_f32 v15, v28, v63, v15
	ml_mul_f32 v64, v10, v53
	ml_fma_f32 v10, v1, v64, v10
	ml_mul_f32 v65, v11, v40
	ml_fma_f32 v11, v28, v65, v11
	ml_mul_f32 v66, v6, v53
	ml_fma_f32 v6, v1, v66, v6
	ml_mul_f32 v67, v7, v40
	ml_fma_f32 v7, v28, v67, v7
	ml_mul_f32 v69, v3, v40
	ml_fma_f32 v3, v28, v69, v3
	ml_mul_f32 v28, v2, v53
	ml_fma_f32 v2, v1, v28, v2
	ml_fma_f32 v70, v32, v68, v0
	ml_mov_b32 v0, 0x1054
	ml_mov_b32 v1, 0x5410
	ml_csel_b32 v1, v1, v0, tcr
	ml_mov_b32 v0, 0x7632
	ml_csel_b32 v0, v0, v71, tcr
	ml_mul_f32 v71, v36, v39
	ml_fma_f32 v32, v32, v71, v36
	ml_fma_f32 v32, v32, v39, v71
	ml_mov_b32 v36, 0x99
	ml_cmp_class_f32 tcr, v71, v36
	ml_csel_b32 v32, v71, v32, tcr
	ml_fma_f32 v29, v29, v37, v41
	ml_cmp_class_f32 tcr, v41, v36
	ml_csel_b32 v29, v41, v29, tcr
	ml_fma_f32 v24, v24, v39, v42
	ml_cmp_class_f32 tcr, v42, v36
	ml_csel_b32 v24, v42, v24, tcr
	ml_fma_f32 v25, v25, v37, v43
	ml_cmp_class_f32 tcr, v43, v36
	ml_csel_b32 v25, v43, v25, tcr
	ml_fma_f32 v20, v20, v39, v44
	ml_cmp_class_f32 tcr, v44, v36
	ml_csel_b32 v20, v44, v20, tcr
	ml_fma_f32 v21, v21, v37, v45
	ml_cmp_class_f32 tcr, v45, v36
	ml_csel_b32 v21, v45, v21, tcr
	ml_fma_f32 v16, v16, v39, v46
	ml_cmp_class_f32 tcr, v46, v36
	ml_csel_b32 v16, v46, v16, tcr
	ml_fma_f32 v17, v17, v37, v47
	ml_cmp_class_f32 tcr, v47, v36
	ml_csel_b32 v17, v47, v17, tcr
	ml_fma_f32 v12, v12, v39, v48
	ml_cmp_class_f32 tcr, v48, v36
	ml_csel_b32 v12, v48, v12, tcr
	ml_fma_f32 v13, v13, v37, v49
	ml_cmp_class_f32 tcr, v49, v36
	ml_csel_b32 v13, v49, v13, tcr
	ml_fma_f32 v8, v8, v39, v50
	ml_cmp_class_f32 tcr, v50, v36
	ml_csel_b32 v8, v50, v8, tcr
	ml_fma_f32 v9, v9, v37, v51
	ml_cmp_class_f32 tcr, v51, v36
	ml_csel_b32 v9, v51, v9, tcr
	ml_fma_f32 v4, v4, v39, v52
	ml_cmp_class_f32 tcr, v52, v36
	ml_csel_b32 v4, v52, v4, tcr
	ml_fma_f32 v5, v5, v37, v35
	ml_cmp_class_f32 tcr, v35, v36
	ml_csel_b32 v5, v35, v5, tcr
	ml_fma_f32 v33, v33, v37, v54
	ml_cmp_class_f32 tcr, v54, v36
	ml_csel_b32 v33, v54, v33, tcr
	ml_fma_f32 v35, v70, v39, v68
	ml_cmp_class_f32 tcr, v68, v36
	ml_csel_b32 v35, v68, v35, tcr
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_cvt_bf16_f32  v35, v35
	ml_cvt_bf16_f32  v33, v33
	ml_byte_permute_b32 v33, v33, v35, s0
	.loc	1 507 20                        ; biv150_konly_encoded_q32.py:507:20
	ml_fma_f32 v30, v30, v53, v55
	ml_cmp_class_f32 tcr, v55, v36
	ml_csel_b32 v30, v55, v30, tcr
	ml_fma_f32 v31, v31, v40, v34
	ml_cmp_class_f32 tcr, v34, v36
	ml_csel_b32 v31, v34, v31, tcr
	ml_fma_f32 v26, v26, v53, v56
	ml_cmp_class_f32 tcr, v56, v36
	ml_csel_b32 v26, v56, v26, tcr
	ml_fma_f32 v27, v27, v40, v57
	ml_cmp_class_f32 tcr, v57, v36
	ml_csel_b32 v27, v57, v27, tcr
	ml_fma_f32 v22, v22, v53, v58
	ml_cmp_class_f32 tcr, v58, v36
	ml_csel_b32 v22, v58, v22, tcr
	ml_fma_f32 v23, v23, v40, v59
	ml_cmp_class_f32 tcr, v59, v36
	ml_csel_b32 v23, v59, v23, tcr
	ml_fma_f32 v18, v18, v53, v60
	ml_cmp_class_f32 tcr, v60, v36
	ml_csel_b32 v18, v60, v18, tcr
	ml_fma_f32 v19, v19, v40, v61
	ml_cmp_class_f32 tcr, v61, v36
	ml_csel_b32 v19, v61, v19, tcr
	ml_fma_f32 v14, v14, v53, v62
	ml_cmp_class_f32 tcr, v62, v36
	ml_csel_b32 v34, v62, v14, tcr
	ml_fma_f32 v14, v15, v40, v63
	ml_cmp_class_f32 tcr, v63, v36
	ml_csel_b32 v15, v63, v14, tcr
	ml_fma_f32 v10, v10, v53, v64
	ml_cmp_class_f32 tcr, v64, v36
	ml_csel_b32 v35, v64, v10, tcr
	ml_fma_f32 v10, v11, v40, v65
	ml_cmp_class_f32 tcr, v65, v36
	ml_csel_b32 v11, v65, v10, tcr
	ml_fma_f32 v6, v6, v53, v66
	ml_cmp_class_f32 tcr, v66, v36
	ml_csel_b32 v37, v66, v6, tcr
	ml_fma_f32 v6, v7, v40, v67
	ml_cmp_class_f32 tcr, v67, v36
	ml_csel_b32 v7, v67, v6, tcr
	ml_fma_f32 v3, v3, v40, v69
	ml_cmp_class_f32 tcr, v69, v36
	ml_csel_b32 v3, v69, v3, tcr
	ml_fma_f32 v2, v2, v53, v28
	ml_cmp_class_f32 tcr, v28, v36
	ml_csel_b32 v2, v28, v2, tcr
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_cvt_bf16_f32  v2, v2
	ml_cvt_bf16_f32  v3, v3
	ml_byte_permute_b32 v3, v3, v2, s0
	ml_cvt_bf16_f32  v2, v32
	ml_cvt_bf16_f32  v6, v29
	ml_byte_permute_b32 v28, v6, v2, s0
	ml_cvt_bf16_f32  v2, v24
	ml_cvt_bf16_f32  v6, v25
	ml_byte_permute_b32 v24, v6, v2, s0
	ml_cvt_bf16_f32  v2, v30
	ml_cvt_bf16_f32  v6, v31
	ml_byte_permute_b32 v25, v6, v2, s0
	ml_cvt_bf16_f32  v2, v26
	ml_cvt_bf16_f32  v6, v27
	ml_byte_permute_b32 v26, v6, v2, s0
	ml_cvt_bf16_f32  v2, v20
	ml_cvt_bf16_f32  v6, v21
	ml_byte_permute_b32 v20, v6, v2, s0
	ml_cvt_bf16_f32  v2, v16
	ml_cvt_bf16_f32  v6, v17
	ml_byte_permute_b32 v21, v6, v2, s0
	.loc	1 198 26                        ; biv150_konly_encoded_q32.py:198:26
	ml_and_b32 v27, tid, 0x30
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_cvt_bf16_f32  v2, v12
	ml_cvt_bf16_f32  v6, v13
	ml_cvt_bf16_f32  v8, v8
	ml_cvt_bf16_f32  v9, v9
	ml_cvt_bf16_f32  v4, v4
	ml_cvt_bf16_f32  v5, v5
	ml_cvt_bf16_f32  v10, v22
	ml_cvt_bf16_f32  v12, v23
	ml_cvt_bf16_f32  v13, v18
	ml_byte_permute_b32 v22, v12, v10, s0
	ml_and_b32 v10, tid, 0x1
	ml_cmp_eq_u32 tcr, v10, 0x0
	ml_and_b32 v10, v38, 0xe
.Ltmp426:
	.loc	1 24 60                         ; biv150_konly_encoded_q32.py:24:60 @[ biv150_konly_encoded_q32.py:238:48 ]
	ml_and_b32 v12, tid, 0x8
.Ltmp427:
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_srl_b32 v12, v12, 0x3
	ml_anyop3_b32 v17, v12, v10, v27, 0xfffffffe
	ml_csel_b32 v10, v28, v24, tcr
	ml_slb_shuffle_rtn_b32 v16, v10, v17
	ml_cvt_bf16_f32  v10, v19
	ml_byte_permute_b32 v13, v10, v13, s0
	ml_csel_b32 v10, v25, v26, tcr
	ml_slb_shuffle_rtn_b32 v14, v10, v17
	ml_cvt_bf16_f32  v18, v34
	ml_byte_permute_b32 v19, v6, v2, s0
	ml_csel_b32 v2, v20, v21, tcr
	ml_slb_shuffle_rtn_b32 v12, v2, v17
	ml_cvt_bf16_f32  v2, v15
	ml_byte_permute_b32 v9, v9, v8, s0
	ml_csel_b32 v6, v22, v13, tcr
	ml_slb_shuffle_rtn_b32 v10, v6, v17
	ml_cvt_bf16_f32  v6, v35
	ml_byte_permute_b32 v23, v2, v18, s0
	ml_csel_b32 v2, v19, v9, tcr
	ml_slb_shuffle_rtn_b32 v8, v2, v17
	ml_cvt_bf16_f32  v2, v11
	ml_byte_permute_b32 v29, v2, v6, s0
	ml_csel_b32 v2, v23, v29, tcr
	ml_slb_shuffle_rtn_b32 v6, v2, v17
	ml_cvt_bf16_f32  v2, v37
	ml_byte_permute_b32 v5, v5, v4, s0
	ml_csel_b32 v4, v5, v33, tcr
	ml_slb_shuffle_rtn_b32 v4, v4, v17
	ml_cvt_bf16_f32  v7, v7
	ml_byte_permute_b32 v30, v7, v2, s0
	ml_csel_b32 v2, v30, v3, tcr
	ml_slb_shuffle_rtn_b32 v2, v2, v17
	ml_csel_b32 v7, v24, v28, tcr
	ml_xor_b32 v24, v17, 0x1
	ml_csel_b32 v5, v33, v5, tcr
	ml_slb_shuffle_rtn_b32 v18, v7, v24
	ml_csel_b32 v7, v26, v25, tcr
	ml_csel_b32 v3, v3, v30, tcr
	.loc	1 203 52                        ; biv150_konly_encoded_q32.py:203:52
	sl_add_i32 s0, s2, s1
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_slb_shuffle_rtn_b32 v17, v7, v24
	ml_csel_b32 v7, v21, v20, tcr
	.loc	1 203 52                        ; biv150_konly_encoded_q32.py:203:52
	sl_add_i32 s2, s75, s1
	.loc	1 206 34                        ; biv150_konly_encoded_q32.py:206:34
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_slb_shuffle_rtn_b32 v15, v7, v24
	ml_csel_b32 v7, v13, v22, tcr
	.loc	1 206 34                        ; biv150_konly_encoded_q32.py:206:34
	sl_sra_b32 {s3, wcr}, s2, 0x1f
	.loc	1 541 29                        ; biv150_konly_encoded_q32.py:541:29
	sl_shl_b64 {s[2:3], wcr}, s[2:3], 0xc
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_slb_shuffle_rtn_b32 v13, v7, v24
	ml_csel_b32 v7, v9, v19, tcr
	.loc	1 541 29                        ; biv150_konly_encoded_q32.py:541:29
	sl_add_i64 s[12:13], s[72:73], s[2:3]
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0xc
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_slb_shuffle_rtn_b32 v11, v7, v24
	ml_csel_b32 v7, v29, v23, tcr
	.loc	1 541 29                        ; biv150_konly_encoded_q32.py:541:29
	sl_add_i64 s[16:17], s[72:73], s[0:1]
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_mov_v2s_b32 s0, v134, 0x12
	ml_slb_shuffle_rtn_b32 v9, v7, v24
	ml_mov_v2s_b32 s1, v134, 0x13
	ml_slb_shuffle_rtn_b32 v7, v5, v24
	.loc	1 198 26                        ; biv150_konly_encoded_q32.py:198:26
	ml_srl_b32 v5, v27, 0x4
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	sl_mov_b64 tcr, s[0:1]
	ml_slb_shuffle_rtn_b32 v3, v3, v24
	sl_cbr_tcraz BB0_63, tcr
; %bb.62:
	.loc	1 0 16 is_stmt 0                ; biv150_konly_encoded_q32.py:0:16
	sl_mov_b32 s0, 0x2010200
	ml_byte_permute_b32 v19, v0, v0, s0
	ml_pk_shl_b16 v19, v19, 0x40004
	ml_byte_permute_b32 v20, v1, v1, s0
	ml_pk_shl_b16 v20, v20, 0x40004
	ml_pk_srl_b8 v20, v20, 0x40004
	sl_wait lmcnt(7)
	ml_byte_permute_b32 v20, v16, v18, v20
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	sl_mull_u32 s0, s14, 0x200
	ml_shl_b32 v21, v5, 0x6
	.loc	1 199 26 is_stmt 1              ; biv150_konly_encoded_q32.py:199:26
	ml_and_b32 v22, tid, 0xf
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_anyop3_b32 v21, s0, v21, v22, 0xfffffffe
	ml_lsa_store_dword v20, s[16:19], unsigned v21, noreg, #0, wb|mie
	ml_pk_srl_b8 v19, v19, 0x40004
	ml_byte_permute_b32 v16, v16, v18, v19
	sl_mov_b32 s0, 0x400
	ml_lsa_store_dword v16, s[16:19], unsigned v21, s0, #0, wb|mie
BB0_63:                                 ; %.critedge
	ml_mov_v2s_b32 s0, v134, 0x14
	ml_mov_v2s_b32 s1, v134, 0x15
	sl_mov_b64 tcr, s[0:1]
	sl_cbr_tcraz BB0_65, tcr
; %bb.64:
	sl_mov_b32 s0, 0x2010200
	sl_wait lmcnt(15)
	ml_byte_permute_b32 v16, v1, v1, s0
	ml_pk_shl_b16 v16, v16, 0x40004
	ml_pk_srl_b8 v16, v16, 0x40004
	sl_wait lmcnt(6)
	ml_byte_permute_b32 v16, v14, v17, v16
	ml_byte_permute_b32 v18, v0, v0, s0
	ml_pk_shl_b16 v18, v18, 0x40004
	sl_mull_u32 s0, s14, 0x200
	ml_shl_b32 v19, v5, 0x6
	.loc	1 199 26                        ; biv150_konly_encoded_q32.py:199:26
	ml_and_b32 v20, tid, 0xf
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_anyop3_b32 v19, s0, v19, v20, 0xfffffffe
	ml_lsa_store_dword v16, s[12:15], unsigned v19, noreg, #0, wb|mie
	ml_pk_srl_b8 v16, v18, 0x40004
	ml_byte_permute_b32 v14, v14, v17, v16
	sl_mov_b32 s0, 0x400
	ml_lsa_store_dword v14, s[12:15], unsigned v19, s0, #0, wb|mie
BB0_65:                                 ; %.critedge2
	ml_mov_v2s_b32 s0, v134, 0x12
	ml_mov_v2s_b32 s1, v134, 0x13
	sl_mov_b64 tcr, s[0:1]
	sl_cbr_tcraz BB0_67, tcr
; %bb.66:
	sl_mov_b32 s0, 0x2010200
	sl_wait lmcnt(14)
	ml_byte_permute_b32 v14, v1, v1, s0
	ml_pk_shl_b16 v14, v14, 0x40004
	ml_pk_srl_b8 v14, v14, 0x40004
	sl_wait lmcnt(5)
	ml_byte_permute_b32 v14, v12, v15, v14
	ml_byte_permute_b32 v16, v0, v0, s0
	ml_pk_shl_b16 v16, v16, 0x40004
	sl_mull_u32 s0, s14, 0x200
	ml_shl_b32 v17, v5, 0x6
	.loc	1 199 26                        ; biv150_konly_encoded_q32.py:199:26
	ml_and_b32 v18, tid, 0xf
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_anyop3_b32 v17, s0, v17, v18, 0xfffffffe
	ml_lsa_store_dword v14, s[16:19], unsigned v17, noreg, #64, wb|mie
	ml_pk_srl_b8 v14, v16, 0x40004
	ml_byte_permute_b32 v12, v12, v15, v14
	sl_mov_b32 s0, 0x400
	ml_lsa_store_dword v12, s[16:19], unsigned v17, s0, #64, wb|mie
BB0_67:                                 ; %.critedge4
	ml_mov_v2s_b32 s0, v134, 0x14
	ml_mov_v2s_b32 s1, v134, 0x15
	sl_mov_b64 tcr, s[0:1]
	sl_cbr_tcraz BB0_69, tcr
; %bb.68:
	sl_mov_b32 s0, 0x2010200
	sl_wait lmcnt(13)
	ml_byte_permute_b32 v12, v1, v1, s0
	ml_pk_shl_b16 v12, v12, 0x40004
	ml_pk_srl_b8 v12, v12, 0x40004
	sl_wait lmcnt(4)
	ml_byte_permute_b32 v12, v10, v13, v12
	ml_byte_permute_b32 v14, v0, v0, s0
	ml_pk_shl_b16 v14, v14, 0x40004
	sl_mull_u32 s0, s14, 0x200
	ml_shl_b32 v15, v5, 0x6
	.loc	1 199 26                        ; biv150_konly_encoded_q32.py:199:26
	ml_and_b32 v16, tid, 0xf
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_anyop3_b32 v15, s0, v15, v16, 0xfffffffe
	ml_lsa_store_dword v12, s[12:15], unsigned v15, noreg, #64, wb|mie
	ml_pk_srl_b8 v12, v14, 0x40004
	ml_byte_permute_b32 v10, v10, v13, v12
	sl_mov_b32 s0, 0x400
	ml_lsa_store_dword v10, s[12:15], unsigned v15, s0, #64, wb|mie
BB0_69:                                 ; %.critedge6
	ml_mov_v2s_b32 s0, v134, 0x12
	ml_mov_v2s_b32 s1, v134, 0x13
	sl_mov_b64 tcr, s[0:1]
	sl_cbr_tcraz BB0_71, tcr
; %bb.70:
	sl_mov_b32 s0, 0x2010200
	sl_wait lmcnt(12)
	ml_byte_permute_b32 v10, v1, v1, s0
	ml_pk_shl_b16 v10, v10, 0x40004
	ml_pk_srl_b8 v10, v10, 0x40004
	sl_wait lmcnt(3)
	ml_byte_permute_b32 v10, v8, v11, v10
	ml_byte_permute_b32 v12, v0, v0, s0
	ml_pk_shl_b16 v12, v12, 0x40004
	sl_mull_u32 s0, s14, 0x200
	ml_shl_b32 v13, v5, 0x6
	.loc	1 199 26                        ; biv150_konly_encoded_q32.py:199:26
	ml_and_b32 v14, tid, 0xf
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_anyop3_b32 v13, s0, v13, v14, 0xfffffffe
	ml_lsa_store_dword v10, s[16:19], unsigned v13, noreg, #128, wb|mie
	ml_pk_srl_b8 v10, v12, 0x40004
	ml_byte_permute_b32 v8, v8, v11, v10
	sl_mov_b32 s0, 0x400
	ml_lsa_store_dword v8, s[16:19], unsigned v13, s0, #128, wb|mie
BB0_71:                                 ; %.critedge8
	ml_mov_v2s_b32 s0, v134, 0x14
	ml_mov_v2s_b32 s1, v134, 0x15
	sl_mov_b64 tcr, s[0:1]
	sl_cbr_tcraz BB0_73, tcr
; %bb.72:
	sl_mov_b32 s0, 0x2010200
	sl_wait lmcnt(11)
	ml_byte_permute_b32 v8, v1, v1, s0
	ml_pk_shl_b16 v8, v8, 0x40004
	ml_pk_srl_b8 v8, v8, 0x40004
	sl_wait lmcnt(2)
	ml_byte_permute_b32 v8, v6, v9, v8
	ml_byte_permute_b32 v10, v0, v0, s0
	ml_pk_shl_b16 v10, v10, 0x40004
	sl_mull_u32 s0, s14, 0x200
	ml_shl_b32 v11, v5, 0x6
	.loc	1 199 26                        ; biv150_konly_encoded_q32.py:199:26
	ml_and_b32 v12, tid, 0xf
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_anyop3_b32 v11, s0, v11, v12, 0xfffffffe
	ml_lsa_store_dword v8, s[12:15], unsigned v11, noreg, #128, wb|mie
	ml_pk_srl_b8 v8, v10, 0x40004
	ml_byte_permute_b32 v6, v6, v9, v8
	sl_mov_b32 s0, 0x400
	ml_lsa_store_dword v6, s[12:15], unsigned v11, s0, #128, wb|mie
BB0_73:                                 ; %.critedge10
	ml_mov_v2s_b32 s0, v134, 0x12
	ml_mov_v2s_b32 s1, v134, 0x13
	sl_mov_b64 tcr, s[0:1]
	sl_cbr_tcraz BB0_75, tcr
; %bb.74:
	sl_mov_b32 s0, 0x2010200
	sl_wait lmcnt(10)
	ml_byte_permute_b32 v6, v1, v1, s0
	ml_pk_shl_b16 v6, v6, 0x40004
	ml_pk_srl_b8 v6, v6, 0x40004
	sl_wait lmcnt(1)
	ml_byte_permute_b32 v6, v4, v7, v6
	ml_byte_permute_b32 v8, v0, v0, s0
	ml_pk_shl_b16 v8, v8, 0x40004
	sl_mull_u32 s0, s14, 0x200
	ml_shl_b32 v9, v5, 0x6
	.loc	1 199 26                        ; biv150_konly_encoded_q32.py:199:26
	ml_and_b32 v10, tid, 0xf
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_anyop3_b32 v9, s0, v9, v10, 0xfffffffe
	ml_lsa_store_dword v6, s[16:19], unsigned v9, noreg, #192, wb|mie
	ml_pk_srl_b8 v6, v8, 0x40004
	ml_byte_permute_b32 v4, v4, v7, v6
	sl_mov_b32 s0, 0x400
	ml_lsa_store_dword v4, s[16:19], unsigned v9, s0, #192, wb|mie
BB0_75:                                 ; %.critedge12
	ml_mov_v2s_b32 s0, v134, 0x14
	ml_mov_v2s_b32 s1, v134, 0x15
	sl_mov_b64 tcr, s[0:1]
	sl_cbr_tcraz BB0_77, tcr
; %bb.76:
	sl_mov_b32 s0, 0x2010200
	ml_byte_permute_b32 v1, v1, v1, s0
	ml_pk_shl_b16 v1, v1, 0x40004
	ml_pk_srl_b8 v1, v1, 0x40004
	sl_wait lmcnt(0)
	ml_byte_permute_b32 v1, v2, v3, v1
	ml_byte_permute_b32 v0, v0, v0, s0
	ml_pk_shl_b16 v0, v0, 0x40004
	ml_mov_v2s_b32 s0, v133, 0x0
	ml_shl_b32 v4, v5, 0x6
	.loc	1 199 26                        ; biv150_konly_encoded_q32.py:199:26
	ml_and_b32 v5, tid, 0xf
	.loc	1 542 16                        ; biv150_konly_encoded_q32.py:542:16
	ml_pk_srl_b8 v0, v0, 0x40004
	sl_mull_u32 s0, s0, 0x200
	ml_anyop3_b32 v4, s0, v4, v5, 0xfffffffe
	ml_lsa_store_dword v1, s[12:15], unsigned v4, noreg, #192, wb|mie
	ml_byte_permute_b32 v0, v2, v3, v0
	sl_mov_b32 s0, 0x400
	ml_lsa_store_dword v0, s[12:15], unsigned v4, s0, #192, wb|mie
BB0_77:                                 ; %common.ret
	.loc	1 0 0 is_stmt 0                 ; biv150_konly_encoded_q32.py:0
	sl_eop 
.Ltmp428:
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	kernel_cjj_konly_q32.kd
	.type	kernel_cjj_konly_q32.kd,@object
	.size	kernel_cjj_konly_q32.kd, 64
kernel_cjj_konly_q32.kd:
	.asciz	"\000\000\000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	kernel_cjj_konly_q32@rel64-kernel_cjj_konly_q32.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	537377
	.asciz	"\003\000\264\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	kernel_cjj_konly_q32, .Lfunc_end0-kernel_cjj_konly_q32
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 32232
; NumSgprs: 104
; NumVgprs: 135
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 12
; VGPRBlocks: 33
; NumSGPRsForWarpsPerNU: 100
; NumVGPRsForWarpsPerNR: 135
; ReqNTIDx: 0
; MaxNTIDx: 0
; MinCTASm: 0
; ActiveWarp: 1
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
	.byte	7                               ; Abbreviation Code
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
	.long	405                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0x18e DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"biv150_konly_encoded_q32.py"   ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/workspace/experiments/minicpm-s2/code/native-k8-sme-mixed-20261029T205801248145Z-A/vllm_fl/patches" ; DW_AT_comp_dir
	.byte	0
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.byte	2                               ; Abbrev [2] 0xa9:0x17 DW_TAG_subprogram
	.ascii	"kernel_cjj_konly_q32"          ; DW_AT_name
	.byte	0
	.byte	1                               ; DW_AT_inline
	.byte	3                               ; Abbrev [3] 0xc0:0xd8 DW_TAG_subprogram
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.long	169                             ; DW_AT_abstract_origin
	.byte	4                               ; Abbrev [4] 0xd5:0x25 DW_TAG_inlined_subroutine
	.long	169                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges0                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	179                             ; DW_AT_call_line
	.byte	73                              ; DW_AT_call_column
	.byte	5                               ; Abbrev [5] 0xe1:0x18 DW_TAG_inlined_subroutine
	.long	169                             ; DW_AT_abstract_origin
	.quad	.Ltmp1                          ; DW_AT_low_pc
	.quad	.Ltmp2                          ; DW_AT_high_pc
	.byte	2                               ; DW_AT_call_file
	.byte	67                              ; DW_AT_call_line
	.byte	68                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	4                               ; Abbrev [4] 0xfa:0x26 DW_TAG_inlined_subroutine
	.long	169                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges1                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	238                             ; DW_AT_call_line
	.byte	48                              ; DW_AT_call_column
	.byte	4                               ; Abbrev [4] 0x106:0x19 DW_TAG_inlined_subroutine
	.long	169                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges2                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	14                              ; DW_AT_call_line
	.byte	39                              ; DW_AT_call_column
	.byte	6                               ; Abbrev [6] 0x112:0xc DW_TAG_inlined_subroutine
	.long	169                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges3                 ; DW_AT_ranges
	.byte	3                               ; DW_AT_call_file
	.byte	213                             ; DW_AT_call_line
	.byte	40                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	0                               ; End Of Children Mark
	.byte	7                               ; Abbrev [7] 0x120:0x1a DW_TAG_inlined_subroutine
	.long	169                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges4                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.short	281                             ; DW_AT_call_line
	.byte	8                               ; DW_AT_call_column
	.byte	6                               ; Abbrev [6] 0x12d:0xc DW_TAG_inlined_subroutine
	.long	169                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges5                 ; DW_AT_ranges
	.byte	2                               ; DW_AT_call_file
	.byte	193                             ; DW_AT_call_line
	.byte	44                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	8                               ; Abbrev [8] 0x13a:0xd DW_TAG_inlined_subroutine
	.long	169                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges6                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.short	396                             ; DW_AT_call_line
	.byte	12                              ; DW_AT_call_column
	.byte	7                               ; Abbrev [7] 0x147:0x43 DW_TAG_inlined_subroutine
	.long	169                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges7                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.short	424                             ; DW_AT_call_line
	.byte	44                              ; DW_AT_call_column
	.byte	7                               ; Abbrev [7] 0x154:0x1a DW_TAG_inlined_subroutine
	.long	169                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges8                 ; DW_AT_ranges
	.byte	2                               ; DW_AT_call_file
	.short	406                             ; DW_AT_call_line
	.byte	31                              ; DW_AT_call_column
	.byte	6                               ; Abbrev [6] 0x161:0xc DW_TAG_inlined_subroutine
	.long	169                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges9                 ; DW_AT_ranges
	.byte	3                               ; DW_AT_call_file
	.byte	213                             ; DW_AT_call_line
	.byte	40                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	7                               ; Abbrev [7] 0x16e:0x1b DW_TAG_inlined_subroutine
	.long	169                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges10                ; DW_AT_ranges
	.byte	2                               ; DW_AT_call_file
	.short	413                             ; DW_AT_call_line
	.byte	17                              ; DW_AT_call_column
	.byte	8                               ; Abbrev [8] 0x17b:0xd DW_TAG_inlined_subroutine
	.long	169                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges11                ; DW_AT_ranges
	.byte	3                               ; DW_AT_call_file
	.short	315                             ; DW_AT_call_line
	.byte	36                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	0                               ; End Of Children Mark
	.byte	8                               ; Abbrev [8] 0x18a:0xd DW_TAG_inlined_subroutine
	.long	169                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges12                ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.short	360                             ; DW_AT_call_line
	.byte	25                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	0                               ; End Of Children Mark
	.section	.debug_ranges,"",@progbits
.Ldebug_ranges0:
	.quad	.Ltmp1-.Lfunc_begin0
	.quad	.Ltmp3-.Lfunc_begin0
	.quad	.Ltmp4-.Lfunc_begin0
	.quad	.Ltmp5-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges1:
	.quad	.Ltmp6-.Lfunc_begin0
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
	.quad	.Ltmp269-.Lfunc_begin0
	.quad	.Ltmp270-.Lfunc_begin0
	.quad	.Ltmp383-.Lfunc_begin0
	.quad	.Ltmp384-.Lfunc_begin0
	.quad	.Ltmp385-.Lfunc_begin0
	.quad	.Ltmp386-.Lfunc_begin0
	.quad	.Ltmp397-.Lfunc_begin0
	.quad	.Ltmp398-.Lfunc_begin0
	.quad	.Ltmp426-.Lfunc_begin0
	.quad	.Ltmp427-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges2:
	.quad	.Ltmp7-.Lfunc_begin0
	.quad	.Ltmp9-.Lfunc_begin0
	.quad	.Ltmp10-.Lfunc_begin0
	.quad	.Ltmp12-.Lfunc_begin0
	.quad	.Ltmp13-.Lfunc_begin0
	.quad	.Ltmp15-.Lfunc_begin0
	.quad	.Ltmp16-.Lfunc_begin0
	.quad	.Ltmp18-.Lfunc_begin0
	.quad	.Ltmp19-.Lfunc_begin0
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
	.quad	.Ltmp36-.Lfunc_begin0
	.quad	.Ltmp37-.Lfunc_begin0
	.quad	.Ltmp39-.Lfunc_begin0
	.quad	.Ltmp40-.Lfunc_begin0
	.quad	.Ltmp58-.Lfunc_begin0
	.quad	.Ltmp59-.Lfunc_begin0
	.quad	.Ltmp61-.Lfunc_begin0
	.quad	.Ltmp62-.Lfunc_begin0
	.quad	.Ltmp63-.Lfunc_begin0
	.quad	.Ltmp64-.Lfunc_begin0
	.quad	.Ltmp69-.Lfunc_begin0
	.quad	.Ltmp70-.Lfunc_begin0
	.quad	.Ltmp72-.Lfunc_begin0
	.quad	.Ltmp73-.Lfunc_begin0
	.quad	.Ltmp75-.Lfunc_begin0
	.quad	.Ltmp76-.Lfunc_begin0
	.quad	.Ltmp110-.Lfunc_begin0
	.quad	.Ltmp111-.Lfunc_begin0
	.quad	.Ltmp113-.Lfunc_begin0
	.quad	.Ltmp114-.Lfunc_begin0
	.quad	.Ltmp116-.Lfunc_begin0
	.quad	.Ltmp117-.Lfunc_begin0
	.quad	.Ltmp119-.Lfunc_begin0
	.quad	.Ltmp120-.Lfunc_begin0
	.quad	.Ltmp122-.Lfunc_begin0
	.quad	.Ltmp123-.Lfunc_begin0
	.quad	.Ltmp124-.Lfunc_begin0
	.quad	.Ltmp125-.Lfunc_begin0
	.quad	.Ltmp126-.Lfunc_begin0
	.quad	.Ltmp127-.Lfunc_begin0
	.quad	.Ltmp128-.Lfunc_begin0
	.quad	.Ltmp129-.Lfunc_begin0
	.quad	.Ltmp166-.Lfunc_begin0
	.quad	.Ltmp167-.Lfunc_begin0
	.quad	.Ltmp169-.Lfunc_begin0
	.quad	.Ltmp170-.Lfunc_begin0
	.quad	.Ltmp172-.Lfunc_begin0
	.quad	.Ltmp173-.Lfunc_begin0
	.quad	.Ltmp176-.Lfunc_begin0
	.quad	.Ltmp177-.Lfunc_begin0
	.quad	.Ltmp179-.Lfunc_begin0
	.quad	.Ltmp180-.Lfunc_begin0
	.quad	.Ltmp181-.Lfunc_begin0
	.quad	.Ltmp182-.Lfunc_begin0
	.quad	.Ltmp184-.Lfunc_begin0
	.quad	.Ltmp185-.Lfunc_begin0
	.quad	.Ltmp197-.Lfunc_begin0
	.quad	.Ltmp198-.Lfunc_begin0
	.quad	.Ltmp212-.Lfunc_begin0
	.quad	.Ltmp213-.Lfunc_begin0
	.quad	.Ltmp217-.Lfunc_begin0
	.quad	.Ltmp218-.Lfunc_begin0
	.quad	.Ltmp220-.Lfunc_begin0
	.quad	.Ltmp221-.Lfunc_begin0
	.quad	.Ltmp226-.Lfunc_begin0
	.quad	.Ltmp227-.Lfunc_begin0
	.quad	.Ltmp236-.Lfunc_begin0
	.quad	.Ltmp237-.Lfunc_begin0
	.quad	.Ltmp238-.Lfunc_begin0
	.quad	.Ltmp383-.Lfunc_begin0
	.quad	.Ltmp384-.Lfunc_begin0
	.quad	.Ltmp385-.Lfunc_begin0
	.quad	.Ltmp386-.Lfunc_begin0
	.quad	.Ltmp397-.Lfunc_begin0
	.quad	.Ltmp398-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges3:
	.quad	.Ltmp7-.Lfunc_begin0
	.quad	.Ltmp8-.Lfunc_begin0
	.quad	.Ltmp10-.Lfunc_begin0
	.quad	.Ltmp11-.Lfunc_begin0
	.quad	.Ltmp13-.Lfunc_begin0
	.quad	.Ltmp14-.Lfunc_begin0
	.quad	.Ltmp16-.Lfunc_begin0
	.quad	.Ltmp17-.Lfunc_begin0
	.quad	.Ltmp19-.Lfunc_begin0
	.quad	.Ltmp20-.Lfunc_begin0
	.quad	.Ltmp22-.Lfunc_begin0
	.quad	.Ltmp23-.Lfunc_begin0
	.quad	.Ltmp26-.Lfunc_begin0
	.quad	.Ltmp27-.Lfunc_begin0
	.quad	.Ltmp30-.Lfunc_begin0
	.quad	.Ltmp31-.Lfunc_begin0
	.quad	.Ltmp34-.Lfunc_begin0
	.quad	.Ltmp35-.Lfunc_begin0
	.quad	.Ltmp37-.Lfunc_begin0
	.quad	.Ltmp38-.Lfunc_begin0
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
	.quad	.Ltmp59-.Lfunc_begin0
	.quad	.Ltmp60-.Lfunc_begin0
	.quad	.Ltmp62-.Lfunc_begin0
	.quad	.Ltmp63-.Lfunc_begin0
	.quad	.Ltmp65-.Lfunc_begin0
	.quad	.Ltmp66-.Lfunc_begin0
	.quad	.Ltmp67-.Lfunc_begin0
	.quad	.Ltmp68-.Lfunc_begin0
	.quad	.Ltmp70-.Lfunc_begin0
	.quad	.Ltmp71-.Lfunc_begin0
	.quad	.Ltmp73-.Lfunc_begin0
	.quad	.Ltmp74-.Lfunc_begin0
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
	.quad	.Ltmp111-.Lfunc_begin0
	.quad	.Ltmp112-.Lfunc_begin0
	.quad	.Ltmp114-.Lfunc_begin0
	.quad	.Ltmp115-.Lfunc_begin0
	.quad	.Ltmp117-.Lfunc_begin0
	.quad	.Ltmp118-.Lfunc_begin0
	.quad	.Ltmp120-.Lfunc_begin0
	.quad	.Ltmp121-.Lfunc_begin0
	.quad	.Ltmp123-.Lfunc_begin0
	.quad	.Ltmp124-.Lfunc_begin0
	.quad	.Ltmp127-.Lfunc_begin0
	.quad	.Ltmp128-.Lfunc_begin0
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
	.quad	.Ltmp167-.Lfunc_begin0
	.quad	.Ltmp168-.Lfunc_begin0
	.quad	.Ltmp170-.Lfunc_begin0
	.quad	.Ltmp171-.Lfunc_begin0
	.quad	.Ltmp173-.Lfunc_begin0
	.quad	.Ltmp174-.Lfunc_begin0
	.quad	.Ltmp175-.Lfunc_begin0
	.quad	.Ltmp176-.Lfunc_begin0
	.quad	.Ltmp177-.Lfunc_begin0
	.quad	.Ltmp178-.Lfunc_begin0
	.quad	.Ltmp180-.Lfunc_begin0
	.quad	.Ltmp181-.Lfunc_begin0
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
	.quad	.Ltmp213-.Lfunc_begin0
	.quad	.Ltmp214-.Lfunc_begin0
	.quad	.Ltmp215-.Lfunc_begin0
	.quad	.Ltmp216-.Lfunc_begin0
	.quad	.Ltmp218-.Lfunc_begin0
	.quad	.Ltmp219-.Lfunc_begin0
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
	.quad	0
	.quad	0
.Ldebug_ranges4:
	.quad	.Ltmp262-.Lfunc_begin0
	.quad	.Ltmp263-.Lfunc_begin0
	.quad	.Ltmp264-.Lfunc_begin0
	.quad	.Ltmp266-.Lfunc_begin0
	.quad	.Ltmp267-.Lfunc_begin0
	.quad	.Ltmp268-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges5:
	.quad	.Ltmp265-.Lfunc_begin0
	.quad	.Ltmp266-.Lfunc_begin0
	.quad	.Ltmp267-.Lfunc_begin0
	.quad	.Ltmp268-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges6:
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
	.quad	0
	.quad	0
.Ldebug_ranges7:
	.quad	.Ltmp309-.Lfunc_begin0
	.quad	.Ltmp353-.Lfunc_begin0
	.quad	.Ltmp354-.Lfunc_begin0
	.quad	.Ltmp360-.Lfunc_begin0
	.quad	.Ltmp361-.Lfunc_begin0
	.quad	.Ltmp362-.Lfunc_begin0
	.quad	.Ltmp363-.Lfunc_begin0
	.quad	.Ltmp366-.Lfunc_begin0
	.quad	.Ltmp384-.Lfunc_begin0
	.quad	.Ltmp385-.Lfunc_begin0
	.quad	.Ltmp386-.Lfunc_begin0
	.quad	.Ltmp387-.Lfunc_begin0
	.quad	.Ltmp388-.Lfunc_begin0
	.quad	.Ltmp397-.Lfunc_begin0
	.quad	.Ltmp398-.Lfunc_begin0
	.quad	.Ltmp413-.Lfunc_begin0
	.quad	.Ltmp414-.Lfunc_begin0
	.quad	.Ltmp417-.Lfunc_begin0
	.quad	.Ltmp418-.Lfunc_begin0
	.quad	.Ltmp419-.Lfunc_begin0
	.quad	.Ltmp420-.Lfunc_begin0
	.quad	.Ltmp422-.Lfunc_begin0
	.quad	.Ltmp423-.Lfunc_begin0
	.quad	.Ltmp425-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges8:
	.quad	.Ltmp309-.Lfunc_begin0
	.quad	.Ltmp342-.Lfunc_begin0
	.quad	.Ltmp343-.Lfunc_begin0
	.quad	.Ltmp344-.Lfunc_begin0
	.quad	.Ltmp345-.Lfunc_begin0
	.quad	.Ltmp346-.Lfunc_begin0
	.quad	.Ltmp347-.Lfunc_begin0
	.quad	.Ltmp348-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges9:
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
	.quad	0
	.quad	0
.Ldebug_ranges10:
	.quad	.Ltmp349-.Lfunc_begin0
	.quad	.Ltmp350-.Lfunc_begin0
	.quad	.Ltmp351-.Lfunc_begin0
	.quad	.Ltmp352-.Lfunc_begin0
	.quad	.Ltmp355-.Lfunc_begin0
	.quad	.Ltmp356-.Lfunc_begin0
	.quad	.Ltmp357-.Lfunc_begin0
	.quad	.Ltmp358-.Lfunc_begin0
	.quad	.Ltmp359-.Lfunc_begin0
	.quad	.Ltmp360-.Lfunc_begin0
	.quad	.Ltmp364-.Lfunc_begin0
	.quad	.Ltmp365-.Lfunc_begin0
	.quad	.Ltmp384-.Lfunc_begin0
	.quad	.Ltmp385-.Lfunc_begin0
	.quad	.Ltmp386-.Lfunc_begin0
	.quad	.Ltmp387-.Lfunc_begin0
	.quad	.Ltmp388-.Lfunc_begin0
	.quad	.Ltmp397-.Lfunc_begin0
	.quad	.Ltmp398-.Lfunc_begin0
	.quad	.Ltmp411-.Lfunc_begin0
	.quad	.Ltmp412-.Lfunc_begin0
	.quad	.Ltmp413-.Lfunc_begin0
	.quad	.Ltmp414-.Lfunc_begin0
	.quad	.Ltmp415-.Lfunc_begin0
	.quad	.Ltmp416-.Lfunc_begin0
	.quad	.Ltmp417-.Lfunc_begin0
	.quad	.Ltmp418-.Lfunc_begin0
	.quad	.Ltmp419-.Lfunc_begin0
	.quad	.Ltmp420-.Lfunc_begin0
	.quad	.Ltmp421-.Lfunc_begin0
	.quad	.Ltmp423-.Lfunc_begin0
	.quad	.Ltmp424-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges11:
	.quad	.Ltmp349-.Lfunc_begin0
	.quad	.Ltmp350-.Lfunc_begin0
	.quad	.Ltmp351-.Lfunc_begin0
	.quad	.Ltmp352-.Lfunc_begin0
	.quad	.Ltmp355-.Lfunc_begin0
	.quad	.Ltmp356-.Lfunc_begin0
	.quad	.Ltmp357-.Lfunc_begin0
	.quad	.Ltmp358-.Lfunc_begin0
	.quad	.Ltmp359-.Lfunc_begin0
	.quad	.Ltmp360-.Lfunc_begin0
	.quad	.Ltmp364-.Lfunc_begin0
	.quad	.Ltmp365-.Lfunc_begin0
	.quad	.Ltmp389-.Lfunc_begin0
	.quad	.Ltmp390-.Lfunc_begin0
	.quad	.Ltmp391-.Lfunc_begin0
	.quad	.Ltmp392-.Lfunc_begin0
	.quad	.Ltmp393-.Lfunc_begin0
	.quad	.Ltmp394-.Lfunc_begin0
	.quad	.Ltmp395-.Lfunc_begin0
	.quad	.Ltmp396-.Lfunc_begin0
	.quad	.Ltmp398-.Lfunc_begin0
	.quad	.Ltmp399-.Lfunc_begin0
	.quad	.Ltmp400-.Lfunc_begin0
	.quad	.Ltmp401-.Lfunc_begin0
	.quad	.Ltmp402-.Lfunc_begin0
	.quad	.Ltmp403-.Lfunc_begin0
	.quad	.Ltmp404-.Lfunc_begin0
	.quad	.Ltmp405-.Lfunc_begin0
	.quad	.Ltmp406-.Lfunc_begin0
	.quad	.Ltmp407-.Lfunc_begin0
	.quad	.Ltmp408-.Lfunc_begin0
	.quad	.Ltmp409-.Lfunc_begin0
	.quad	.Ltmp410-.Lfunc_begin0
	.quad	.Ltmp411-.Lfunc_begin0
	.quad	.Ltmp412-.Lfunc_begin0
	.quad	.Ltmp413-.Lfunc_begin0
	.quad	.Ltmp414-.Lfunc_begin0
	.quad	.Ltmp415-.Lfunc_begin0
	.quad	.Ltmp420-.Lfunc_begin0
	.quad	.Ltmp421-.Lfunc_begin0
	.quad	.Ltmp423-.Lfunc_begin0
	.quad	.Ltmp424-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges12:
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
      - .address_space:  global
        .name:           KArg_6
        .offset:         48
        .size:           8
        .value_kind:     global_buffer
      - .name:           KArg_7
        .offset:         56
        .size:           4
        .value_kind:     by_value
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
      - .name:           KArg_10
        .offset:         80
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_11
        .offset:         84
        .size:           4
        .value_kind:     by_value
      - .name:           KArg_12
        .offset:         88
        .size:           8
        .value_kind:     by_value
      - .address_space:  global
        .name:           KArg_13
        .offset:         96
        .size:           8
        .value_kind:     global_buffer
      - .name:           KArg_14
        .offset:         104
        .size:           4
        .value_kind:     by_value
      - .address_space:  global
        .name:           KArg_15
        .offset:         112
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_16
        .offset:         120
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_17
        .offset:         128
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_18
        .offset:         136
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .name:           KArg_19
        .offset:         144
        .size:           8
        .value_kind:     global_buffer
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
      - .name:           KArg_23
        .offset:         176
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_24
        .offset:         184
        .size:           8
        .value_kind:     by_value
      - .name:           KArg_25
        .offset:         192
        .size:           8
        .value_kind:     by_value
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
    .group_segment_fixed_size: 0
    .kernarg_segment_align: 8
    .kernarg_segment_size: 216
    .max_flat_workgroup_size: 0
    .name:           kernel_cjj_konly_q32
    .private_segment_fixed_size: 0
    .sgpr_count:     104
    .sgpr_spill_count: 98
    .symbol:         kernel_cjj_konly_q32.kd
    .vgpr_count:     135
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
