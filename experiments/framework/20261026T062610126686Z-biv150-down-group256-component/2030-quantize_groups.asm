	.text
	.globl	quantize_groups                 ; -- Begin function quantize_groups
	.p2align	3
	.type	quantize_groups,@function
	.iluvatar_kernel quantize_groups
quantize_groups:                        ; @quantize_groups
.Lfunc_begin0:
	.file	1 "/workspace/experiments/minicpm-s2/framework/20261026T062610126686Z-biv150-down-group256-component/source" "candidate.py"
	.loc	1 15 0                          ; candidate.py:15:0
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
		granulated_workitem_vgpr_count = 1
		granulated_warp_sgpr_count = 3
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
		kernarg_segment_byte_size = 40
		workgroup_fbarrier_count = 0
		warp_sgpr_count = 32
		workitem_vgpr_count = 8
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
	ml_vrf_init_u32 v1, tcr
.Ltmp0:
	.loc	1 19 21 prologue_end            ; candidate.py:19:21
	ml_mov_b32 v0, tid
	.loc	1 17 24                         ; candidate.py:17:24
	sl_lsa_load_b32x16 s[12:27], s[4:5], noreg, #0, ca
	.loc	1 19 21                         ; candidate.py:19:21
	ml_and_b32 v1, v1, 0xff
	.loc	1 20 30                         ; candidate.py:20:30
	sl_mov_b32 s3, 0x0
	.loc	1 20 42 is_stmt 0               ; candidate.py:20:42
	sl_wait smcnt(0)
	sl_mov_b32 s23, 0xfff00002
	.loc	1 20 26                         ; candidate.py:20:26
	sl_mull_u32 s4, s6, 0x1800
	.loc	1 20 30                         ; candidate.py:20:30
	sl_mull_u32 s2, s7, 0x200
	.loc	1 20 20                         ; candidate.py:20:20
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[4:5], 0x1
.Ltmp1:
	.file	2 "/usr/local/lib/python3.12/site-packages/triton/language" "standard.py"
	.loc	2 213 40 is_stmt 1              ; standard.py:213:40 @[ candidate.py:21:40 ]
	ml_xor_b32 v3, tid, 0x20
	ml_xor_b32 v5, tid, 0x10
	ml_cmp_eq_u32 tcr, tid, 0x0
.Ltmp2:
	.loc	1 20 20                         ; candidate.py:20:20
	sl_add_i64 s[0:1], s[12:13], s[0:1]
	.loc	1 20 30 is_stmt 0               ; candidate.py:20:30
	sl_add_i64 s[20:21], s[0:1], s[2:3]
	.loc	1 20 48                         ; candidate.py:20:48
	ml_lsa_load_ushort v2, s[20:23], unsigned v1, noreg, #0, ca|mie
	.loc	1 19 21 is_stmt 1               ; candidate.py:19:21
	ml_mov_v2s_b32 s0, v1, 0x0
	sl_srl_b32 {s12, wcr}, s0, 0x6
	.loc	1 20 48                         ; candidate.py:20:48
	sl_wait vmcnt(0)
	ml_shl_b32 v2, v2, 0x10
	.loc	1 21 36                         ; candidate.py:21:36
	ml_abs_f32 v4, v2
.Ltmp3:
	.loc	2 213 40                        ; standard.py:213:40 @[ candidate.py:21:40 ]
	ml_slb_shuffle_rtn_b32 v3, v4, v3
.Ltmp4:
	.loc	2 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ candidate.py:21:40 ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v3, v4, v3
.Ltmp5:
	.loc	2 213 40                        ; standard.py:213:40 @[ candidate.py:21:40 ]
	ml_slb_shuffle_rtn_b32 v4, v3, v5
	ml_xor_b32 v5, tid, 0x8
.Ltmp6:
	.loc	2 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ candidate.py:21:40 ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v3, v3, v4
.Ltmp7:
	.loc	2 213 40                        ; standard.py:213:40 @[ candidate.py:21:40 ]
	ml_slb_shuffle_rtn_b32 v4, v3, v5
	ml_xor_b32 v5, tid, 0x4
.Ltmp8:
	.loc	2 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ candidate.py:21:40 ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v4, v3, v4
.Ltmp9:
	.loc	2 213 40                        ; standard.py:213:40 @[ candidate.py:21:40 ]
	ml_slb_shuffle_rtn_b32 v5, v4, v5
	ml_xor_b32 v3, tid, 0x2
.Ltmp10:
	.loc	2 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ candidate.py:21:40 ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v4, v4, v5
.Ltmp11:
	.loc	2 213 40                        ; standard.py:213:40 @[ candidate.py:21:40 ]
	ml_slb_shuffle_rtn_b32 v5, v4, v3
.Ltmp12:
	.loc	2 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ candidate.py:21:40 ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v6, v4, v5
.Ltmp13:
	.loc	2 213 40                        ; standard.py:213:40 @[ candidate.py:21:40 ]
	ml_xor_b32 v4, tid, 0x1
	ml_slb_shuffle_rtn_b32 v7, v6, v4
	ml_mov_b32 v5, 0x0
	sl_and_savetmsk_b64 {s[0:1], wcr}, tcr, tmsk
	; mask branch BB0_2
BB0_1:
	.loc	2 0 40 is_stmt 0                ; standard.py:0:40
	sl_wait lmcnt(0)
	ml_max_f32 v6, v6, v7
	sl_mull_u32 s2, s12, 0x4
	.loc	2 213 40                        ; standard.py:213:40 @[ candidate.py:21:40 ]
	ml_mov_b32 v7, s2
	ml_slb_store_b32x1  v6, v7, noreg, #0, null
BB0_2:
	.loc	2 0 40                          ; standard.py:0:40
	sl_or_b64 {tmsk, wcr}, tmsk, s[0:1]
	sl_mull_u32 s2, s7, 0x100
	.loc	2 213 40                        ; standard.py:213:40 @[ candidate.py:21:40 ]
	sl_wait lmcnt(0)
	sl_barrier 
	ml_cmp_lt_u32 tcr, v1, 0x4
	ml_shl_b32 v6, v1, 0x2
	sl_mov_b64 s[0:1], tcr
	sl_and_savetmsk_b64 {s[8:9], wcr}, tcr, tmsk
	; mask branch BB0_4
BB0_3:
	ml_slb_load_b32x1  v5, v6, noreg, #0, null
BB0_4:
	.loc	2 0 40                          ; standard.py:0:40
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	2 213 40                        ; standard.py:213:40 @[ candidate.py:21:40 ]
	sl_wait lmcnt(0)
	ml_slb_shuffle_rtn_b32 v3, v5, v3
.Ltmp14:
	.loc	2 192 27 is_stmt 1              ; standard.py:192:27 @[ standard.py:213:40 @[ candidate.py:21:40 ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v3, v5, v3
.Ltmp15:
	.loc	2 213 40                        ; standard.py:213:40 @[ candidate.py:21:40 ]
	ml_slb_shuffle_rtn_b32 v4, v3, v4
	ml_and_b32 v5, tid, 0x3
	ml_cmp_eq_u32 tcr, v5, 0x0
	sl_and_b64 {s[8:9], wcr}, s[0:1], tcr
	sl_and_savetmsk_b64 {s[0:1], wcr}, s[8:9], tmsk
	; mask branch BB0_6
BB0_5:
	.loc	2 0 40 is_stmt 0                ; standard.py:0:40
	sl_wait lmcnt(0)
	ml_max_f32 v3, v3, v4
	.loc	2 213 40                        ; standard.py:213:40 @[ candidate.py:21:40 ]
	ml_slb_store_b32x1  v3, v6, noreg, #0, null
BB0_6:
	.loc	2 0 40                          ; standard.py:0:40
	sl_or_b64 {tmsk, wcr}, tmsk, s[0:1]
	.loc	2 213 40                        ; standard.py:213:40 @[ candidate.py:21:40 ]
	sl_wait lmcnt(0)
	sl_barrier 
	ml_mov_b32 v3, 0x0
	ml_slb_load_b32x1  v3, v3, noreg, #0, null
	ml_mov_b32 v4, 0x358637bd
	ml_mov_b32 v5, 0xc2fe0000
	ml_mov_b32 v6, 0x99
	sl_wait lmcnt(0)
	ml_mov_v2s_b32 s0, v3, 0x0
	ml_mov_b32 v3, 0x3c010204
.Ltmp16:
	.loc	1 21 44 is_stmt 1               ; candidate.py:21:44
	ml_max_f32 v4, s0, v4
	.loc	1 22 28                         ; candidate.py:22:28
	ml_mul_f32 v7, v4, 0x3c010204
	ml_fma_f32 v4, v7, v5, v4
	ml_cmp_class_f32 tcr, v7, v6
	ml_fma_f32 v3, v4, v3, v7
	ml_csel_b32 v3, v7, v3, tcr
	.loc	1 23 21                         ; candidate.py:23:21
	ml_xor_b32 v5, v3, 0x80000000
	ml_rcp_f32 v4, v3
	.loc	1 27 52                         ; candidate.py:27:52
	sl_reg_read s0, hwreg(HW_REG_MODE)
	sl_or_b32 {s1, wcr}, s0, 0x3
	.loc	1 23 21                         ; candidate.py:23:21
	ml_mul_f32 v7, v2, v4
	ml_fma_f32 v2, v5, v7, v2
	ml_cmp_class_f32 tcr, v7, v6
	ml_fma_f32 v2, v4, v2, v7
	ml_csel_b32 v2, v7, v2, tcr
	.loc	1 25 24                         ; candidate.py:25:24
	ml_abs_f32 v4, v2
	.loc	1 25 29 is_stmt 0               ; candidate.py:25:29
	ml_add_f32 v4, v4, 0x3f000000
	.loc	1 26 21 is_stmt 1               ; candidate.py:26:21
	ml_cmp_lt_f32 tcr, v2, 0x0
	.loc	1 25 17                         ; candidate.py:25:17
	ml_floor_f32 v4, v4
	.loc	1 26 25                         ; candidate.py:26:25
	ml_sub_f32 v2, 0, v4
	.loc	1 26 28 is_stmt 0               ; candidate.py:26:28
	ml_csel_b32 v2, v2, v4, tcr
	.loc	1 27 45 is_stmt 1               ; candidate.py:27:45
	ml_max_f32 v2, v2, 0xc2fe0000
	.loc	1 27 26 is_stmt 0               ; candidate.py:27:26
	ml_min_f32 v2, v2, 0x42fe0000
	.loc	1 27 52                         ; candidate.py:27:52
	sl_reg_write hwreg(HW_REG_MODE), s1
	ml_cvt_i32_f32  v2, v2
	sl_reg_write hwreg(HW_REG_MODE), s0
	.loc	1 28 17 is_stmt 1               ; candidate.py:28:17
	sl_add_i64 s[0:1], s[14:15], s[4:5]
	.loc	1 28 27 is_stmt 0               ; candidate.py:28:27
	sl_add_i64 s[0:1], s[0:1], s[2:3]
	.loc	1 28 39                         ; candidate.py:28:39
	ml_addo_u32 {v1, tcr}, s0, v1
	.loc	1 27 52 is_stmt 1               ; candidate.py:27:52
	ml_and_b32 v2, v2, 0xff
	.loc	1 28 42                         ; candidate.py:28:42
	ml_mov_v2s_b32 s0, v1, 0x0
	.loc	1 28 39 is_stmt 0               ; candidate.py:28:39
	ml_mov_b32 v4, s1
	ml_addc_i32 v4, 0, v4, tcr
	.loc	1 28 42                         ; candidate.py:28:42
	ml_mov_v2s_b32 s1, v4, 0x0
	ml_mov_b32 v4, s0
	ml_sub_i32 v1, v1, v4
	sl_mov_b32 s3, 0xffffffff
	sl_mov_b32 s2, s3
	sl_and_savetmsk_b64 {s[10:11], wcr}, s[2:3], tmsk
	ml_lsa_store_byte v2, s[0:3], signed v1, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 29 39 is_stmt 1               ; candidate.py:29:39
	ml_or_b32 v0, s12, v0
	ml_cmp_eq_u32 tcr, v0, 0x0
	sl_mull_u32 s0, s6, 0x18
	sl_sra_b32 {s1, wcr}, s0, 0x1f
	sl_shl_b64 {s[0:1], wcr}, s[0:1], 0x2
	sl_add_i64 s[0:1], s[16:17], s[0:1]
	sl_mull_u32 s2, s7, 0x4
	sl_and_savetmsk_b64 {s[10:11], wcr}, tcr, tmsk
	ml_lsa_store_dword v3, s[0:3], noreg, s2, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[10:11]
	.loc	1 29 4 is_stmt 0                ; candidate.py:29:4
	sl_eop 
.Ltmp17:
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	quantize_groups.kd
	.type	quantize_groups.kd,@object
	.size	quantize_groups.kd, 64
quantize_groups.kd:
	.asciz	"\000\000\000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	quantize_groups@rel64-quantize_groups.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	536769
	.asciz	"\003\000\264\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	quantize_groups, .Lfunc_end0-quantize_groups
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 1072
; NumSgprs: 32
; NumVgprs: 8
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 12
; IeeeMode: 1
; SLBByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 3
; VGPRBlocks: 1
; NumSGPRsForWarpsPerNU: 28
; NumVGPRsForWarpsPerNR: 8
; ReqNTIDx: 0
; MaxNTIDx: 0
; MinCTASm: 0
; ActiveWarp: 8
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
	.long	221                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0xd6 DW_TAG_compile_unit
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
	.byte	2                               ; Abbrev [2] 0x9f:0x12 DW_TAG_subprogram
	.ascii	"quantize_groups"               ; DW_AT_name
	.byte	0
	.byte	1                               ; DW_AT_inline
	.byte	3                               ; Abbrev [3] 0xb1:0x2f DW_TAG_subprogram
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.long	159                             ; DW_AT_abstract_origin
	.byte	4                               ; Abbrev [4] 0xc6:0x19 DW_TAG_inlined_subroutine
	.long	159                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges0                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	21                              ; DW_AT_call_line
	.byte	40                              ; DW_AT_call_column
	.byte	5                               ; Abbrev [5] 0xd2:0xc DW_TAG_inlined_subroutine
	.long	159                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges1                 ; DW_AT_ranges
	.byte	2                               ; DW_AT_call_file
	.byte	213                             ; DW_AT_call_line
	.byte	40                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	0                               ; End Of Children Mark
	.byte	0                               ; End Of Children Mark
	.section	.debug_ranges,"",@progbits
.Ldebug_ranges0:
	.quad	.Ltmp1-.Lfunc_begin0
	.quad	.Ltmp2-.Lfunc_begin0
	.quad	.Ltmp3-.Lfunc_begin0
	.quad	.Ltmp16-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges1:
	.quad	.Ltmp4-.Lfunc_begin0
	.quad	.Ltmp5-.Lfunc_begin0
	.quad	.Ltmp6-.Lfunc_begin0
	.quad	.Ltmp7-.Lfunc_begin0
	.quad	.Ltmp8-.Lfunc_begin0
	.quad	.Ltmp9-.Lfunc_begin0
	.quad	.Ltmp10-.Lfunc_begin0
	.quad	.Ltmp11-.Lfunc_begin0
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
      - .address_space:  global
        .name:           KArg_4
        .offset:         32
        .size:           8
        .value_kind:     global_buffer
    .group_segment_fixed_size: 0
    .kernarg_segment_align: 8
    .kernarg_segment_size: 40
    .max_flat_workgroup_size: 0
    .name:           quantize_groups
    .private_segment_fixed_size: 0
    .sgpr_count:     32
    .sgpr_spill_count: 0
    .symbol:         quantize_groups.kd
    .vgpr_count:     8
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
