	.text
	.globl	probability_reference           ; -- Begin function probability_reference
	.p2align	3
	.type	probability_reference,@function
	.iluvatar_kernel probability_reference
probability_reference:                  ; @probability_reference
.Lfunc_begin0:
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
	.file	1 "/workspace/experiments/minicpm-s2/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/source" "exp2_reference.py"
	.loc	1 7 22 prologue_end             ; exp2_reference.py:7:22
	; Func LiveIn Regs:
	;  blockIdx.x : s6
	sl_lsa_load_b32x16 s[12:27], s[4:5], noreg, #0, ca
	.loc	1 8 23                          ; exp2_reference.py:8:23
	ml_and_b32 v0, tid, 0xf
	.loc	1 9 27                          ; exp2_reference.py:9:27
	sl_mov_b32 s3, 0xfff00004
	.loc	1 9 24 is_stmt 0                ; exp2_reference.py:9:24
	sl_mull_u32 s4, s6, 0x10
	.loc	1 9 20                          ; exp2_reference.py:9:20
	sl_sra_b32 {s5, wcr}, s4, 0x1f
	sl_shl_b64 {s[10:11], wcr}, s[4:5], 0x2
.Ltmp0:
	.file	2 "/usr/local/lib/python3.12/site-packages/triton/language" "standard.py"
	.loc	2 213 40 is_stmt 1              ; standard.py:213:40 @[ exp2_reference.py:10:25 ]
	ml_xor_b32 v2, tid, 0x8
	ml_xor_b32 v3, tid, 0x4
	ml_xor_b32 v4, tid, 0x2
.Ltmp1:
	.loc	1 11 39                         ; exp2_reference.py:11:39
	ml_and_b32 v5, tid, 0x30
	sl_mov_b32 s7, 0xffffffff
	.loc	1 9 20                          ; exp2_reference.py:9:20
	sl_wait smcnt(0)
	sl_add_i64 s[0:1], s[12:13], s[10:11]
	.loc	1 9 14 is_stmt 0                ; exp2_reference.py:9:14
	ml_lsa_load_dword v1, s[0:3], unsigned v0, noreg, #0, ca|mie
	.loc	1 12 19 is_stmt 1               ; exp2_reference.py:12:19
	sl_shl_b64 {s[0:1], wcr}, s[4:5], 0x1
	.loc	1 11 25                         ; exp2_reference.py:11:25
	sl_add_i64 s[2:3], s[14:15], s[10:11]
	.loc	1 12 19                         ; exp2_reference.py:12:19
	sl_add_i64 s[10:11], s[16:17], s[0:1]
	.loc	1 11 32                         ; exp2_reference.py:11:32
	ml_mov_b32 v6, s3
	.loc	1 12 26                         ; exp2_reference.py:12:26
	ml_mov_b32 v7, s11
.Ltmp2:
	.loc	2 213 40                        ; standard.py:213:40 @[ exp2_reference.py:10:25 ]
	sl_wait vmcnt(0)
	ml_slb_shuffle_rtn_b32 v2, v1, v2
.Ltmp3:
	.loc	2 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ exp2_reference.py:10:25 ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v2, v1, v2
.Ltmp4:
	.loc	2 213 40                        ; standard.py:213:40 @[ exp2_reference.py:10:25 ]
	ml_slb_shuffle_rtn_b32 v3, v2, v3
.Ltmp5:
	.loc	2 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ exp2_reference.py:10:25 ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v2, v2, v3
.Ltmp6:
	.loc	2 213 40                        ; standard.py:213:40 @[ exp2_reference.py:10:25 ]
	ml_slb_shuffle_rtn_b32 v3, v2, v4
	ml_xor_b32 v4, tid, 0x1
.Ltmp7:
	.loc	2 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ exp2_reference.py:10:25 ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v2, v2, v3
.Ltmp8:
	.loc	2 213 40                        ; standard.py:213:40 @[ exp2_reference.py:10:25 ]
	ml_slb_shuffle_rtn_b32 v3, v2, v4
.Ltmp9:
	.loc	1 9 27                          ; exp2_reference.py:9:27
	ml_shl_b32 v4, v0, 0x2
	.loc	1 12 26                         ; exp2_reference.py:12:26
	ml_shl_b32 v0, v0, 0x1
	.loc	1 11 32                         ; exp2_reference.py:11:32
	ml_addo_u32 {v4, tcr}, s2, v4
	.loc	1 11 39 is_stmt 0               ; exp2_reference.py:11:39
	ml_mov_v2s_b32 s4, v4, 0x0
	.loc	1 11 32                         ; exp2_reference.py:11:32
	ml_addc_i32 v6, 0, v6, tcr
	.loc	1 11 39                         ; exp2_reference.py:11:39
	ml_cmp_eq_u32 tcr, v5, 0x0
	ml_mov_v2s_b32 s5, v6, 0x0
	sl_mov_b64 s[0:1], tcr
	.loc	1 12 26 is_stmt 1               ; exp2_reference.py:12:26
	ml_addo_u32 {v0, tcr}, s10, v0
.Ltmp10:
	.loc	2 192 27                        ; standard.py:192:27 @[ standard.py:213:40 @[ exp2_reference.py:10:25 ] ]
	sl_wait lmcnt(0)
	ml_max_f32 v2, v2, v3
.Ltmp11:
	.loc	1 10 16                         ; exp2_reference.py:10:16
	ml_sub_f32 v1, v1, v2
	.loc	1 11 39                         ; exp2_reference.py:11:39
	ml_mov_b32 v2, s4
	.loc	1 10 14                         ; exp2_reference.py:10:14
	ml_exp_f32 v1, v1
	.loc	1 11 39                         ; exp2_reference.py:11:39
	ml_sub_i32 v2, v4, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_dword v1, s[4:7], signed v2, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 12 33                         ; exp2_reference.py:12:33
	ml_mov_v2s_b32 s4, v0, 0x0
	.loc	1 12 26 is_stmt 0               ; exp2_reference.py:12:26
	ml_addc_i32 v2, 0, v7, tcr
	.loc	1 12 33                         ; exp2_reference.py:12:33
	ml_mov_v2s_b32 s5, v2, 0x0
	.loc	1 12 38                         ; exp2_reference.py:12:38
	ml_cvt_bf16_f32  v1, v1
	.loc	1 12 33                         ; exp2_reference.py:12:33
	ml_mov_b32 v2, s4
	ml_sub_i32 v0, v0, v2
	sl_and_savetmsk_b64 {s[8:9], wcr}, s[0:1], tmsk
	ml_lsa_store_short v1, s[4:7], signed v0, noreg, #0, wb
	sl_or_b64 {tmsk, wcr}, tmsk, s[8:9]
	.loc	1 12 4                          ; exp2_reference.py:12:4
	sl_eop 
.Ltmp12:
	.section	.rodata,"a",@progbits
	.p2align	6, 0x0
	.globl	probability_reference.kd
	.type	probability_reference.kd,@object
	.size	probability_reference.kd, 64
probability_reference.kd:
	.asciz	"\000\000\000"
	.long	0
	.asciz	"\000\000\000\000\000\000\000"
	.quad	probability_reference@rel64-probability_reference.kd
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
	.long	536769
	.asciz	"\003\000\224\006\211\000\000\000\000\000\000"
	.text
.Lfunc_end0:
	.size	probability_reference, .Lfunc_end0-probability_reference
	.cfi_endproc
                                        ; -- End function
	.section	.Iluvatar.csdata,"",@progbits
; Kernel info:
; codeLenInByte = 472
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
	.long	233                             ; Length of Unit
	.short	2                               ; DWARF version number
	.long	.debug_abbrev                   ; Offset Into Abbrev. Section
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0xe2 DW_TAG_compile_unit
	.ascii	"triton"                        ; DW_AT_producer
	.byte	0
	.short	2                               ; DW_AT_language
	.ascii	"exp2_reference.py"             ; DW_AT_name
	.byte	0
	.long	.debug_line                     ; DW_AT_stmt_list
	.ascii	"/workspace/experiments/minicpm-s2/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/source" ; DW_AT_comp_dir
	.byte	0
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.byte	2                               ; Abbrev [2] 0xa5:0x18 DW_TAG_subprogram
	.ascii	"probability_reference"         ; DW_AT_name
	.byte	0
	.byte	1                               ; DW_AT_inline
	.byte	3                               ; Abbrev [3] 0xbd:0x2f DW_TAG_subprogram
	.quad	.Lfunc_begin0                   ; DW_AT_low_pc
	.quad	.Lfunc_end0                     ; DW_AT_high_pc
	.long	165                             ; DW_AT_abstract_origin
	.byte	4                               ; Abbrev [4] 0xd2:0x19 DW_TAG_inlined_subroutine
	.long	165                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges0                 ; DW_AT_ranges
	.byte	1                               ; DW_AT_call_file
	.byte	10                              ; DW_AT_call_line
	.byte	25                              ; DW_AT_call_column
	.byte	5                               ; Abbrev [5] 0xde:0xc DW_TAG_inlined_subroutine
	.long	165                             ; DW_AT_abstract_origin
	.long	.Ldebug_ranges1                 ; DW_AT_ranges
	.byte	2                               ; DW_AT_call_file
	.byte	213                             ; DW_AT_call_line
	.byte	40                              ; DW_AT_call_column
	.byte	0                               ; End Of Children Mark
	.byte	0                               ; End Of Children Mark
	.byte	0                               ; End Of Children Mark
	.section	.debug_ranges,"",@progbits
.Ldebug_ranges0:
	.quad	.Ltmp0-.Lfunc_begin0
	.quad	.Ltmp1-.Lfunc_begin0
	.quad	.Ltmp2-.Lfunc_begin0
	.quad	.Ltmp9-.Lfunc_begin0
	.quad	.Ltmp10-.Lfunc_begin0
	.quad	.Ltmp11-.Lfunc_begin0
	.quad	0
	.quad	0
.Ldebug_ranges1:
	.quad	.Ltmp3-.Lfunc_begin0
	.quad	.Ltmp4-.Lfunc_begin0
	.quad	.Ltmp5-.Lfunc_begin0
	.quad	.Ltmp6-.Lfunc_begin0
	.quad	.Ltmp7-.Lfunc_begin0
	.quad	.Ltmp8-.Lfunc_begin0
	.quad	.Ltmp10-.Lfunc_begin0
	.quad	.Ltmp11-.Lfunc_begin0
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
    .name:           probability_reference
    .private_segment_fixed_size: 0
    .sgpr_count:     32
    .sgpr_spill_count: 0
    .symbol:         probability_reference.kd
    .vgpr_count:     8
    .vgpr_spill_count: 0
    .warp_size:      64
iluvatar.version:
  - 1
  - 0
...

	.end_iluvatar_hsa_metadata
