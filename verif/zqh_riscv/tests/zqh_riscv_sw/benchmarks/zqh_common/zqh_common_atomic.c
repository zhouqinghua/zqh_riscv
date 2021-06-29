#ifndef __ZQH_COMMON_ATOMIC_C
#define __ZQH_COMMON_ATOMIC_C

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"

uint32_t atomic32_fetch_add_unless(uint32_t counter, uint32_t a, uint32_t u)
{
       uint32_t prev, rc;

	__asm__ __volatile__ (
		"0:	lr.w     %[p],  %[c]\n"
		"	beq      %[p],  %[u], 1f\n"
		"	add      %[rc], %[p], %[a]\n"
		"	sc.w.rl  %[rc], %[rc], %[c]\n"
		"	bnez     %[rc], 0b\n"
		"	fence    rw, rw\n"
		"1:\n"
		: [p]"=&r" (prev), [rc]"=&r" (rc), [c]"+A" (counter)
		: [a]"r" (a), [u]"r" (u)
		: "memory");
	return prev;
}

uint32_t cas32_lr_sc(uint32_t *ptr_v, uint32_t exp_v, uint32_t wr_v)
{
       uint32_t ret_v;

	__asm__ __volatile__ (
		"0:	lr.w     %[ret],  %[ptr]\n"
		"	bne      %[ret],  %[exp], 1f\n"
		"	sc.w     %[ret], %[wr], %[ptr]\n"
		"	j 2f\n"
		"1: li %[ret], 1\n"
		"2: \n"
		: [ret]"=&r" (ret_v), [ptr]"+A" (*ptr_v)
		: [wr]"r" (wr_v), [exp]"r" (exp_v)
		: "memory");
	return ret_v;
}

uint32_t cas32_lr_aq_sc(uint32_t *ptr_v, uint32_t exp_v, uint32_t wr_v)
{
       uint32_t ret_v;

	__asm__ __volatile__ (
		"0:	lr.w.aq  %[ret],  %[ptr]\n"
		"	bne      %[ret],  %[exp], 1f\n"
		"	sc.w     %[ret], %[wr], %[ptr]\n"
		"	j 2f\n"
		"1: li %[ret], 1\n"
		"2: \n"
		: [ret]"=&r" (ret_v), [ptr]"+A" (*ptr_v)
		: [wr]"r" (wr_v), [exp]"r" (exp_v)
		: "memory");
	return ret_v;
}

uint32_t cas32_lr_sc_rl(uint32_t *ptr_v, uint32_t exp_v, uint32_t wr_v)
{
       uint32_t ret_v;

	__asm__ __volatile__ (
		"0:	lr.w     %[ret],  %[ptr]\n"
		"	bne      %[ret],  %[exp], 1f\n"
		"	sc.w.rl  %[ret], %[wr], %[ptr]\n"
		"	j 2f\n"
		"1: li %[ret], 1\n"
		"2: \n"
		: [ret]"=&r" (ret_v), [ptr]"+A" (*ptr_v)
		: [wr]"r" (wr_v), [exp]"r" (exp_v)
		: "memory");
	return ret_v;
}

void swap32_get_lock(uint32_t *ptr_v) {
    uint32_t pre_v;
    uint32_t new_v = 1;
	__asm__ __volatile__ (
        "0: amoswap.w.aq %[pre], %[new], %[ptr]\n" // Attempt to acquire lock.
        "   bnez %[pre], 0b\n" // Retry if held.
		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
		:[new]"r" (new_v)
		:"memory");
    return;
}

void swap32_put_lock(uint32_t *ptr_v) {
	__asm__ __volatile__ (
        "amoswap.w.rl x0, x0, %[ptr]\n"
		:[ptr]"+A" (*ptr_v)
		:
		:"memory");
    return;
}

void cas32_get_lock(uint32_t *ptr_v){
    while(cas32_lr_aq_sc(ptr_v, 0, 1));
}

void cas32_put_lock(uint32_t *ptr_v){
    while(cas32_lr_sc_rl(ptr_v, 1, 0));
}

uint32_t amo32_swap(uint32_t *ptr_v, uint32_t new_v) {
    uint32_t pre_v;
	__asm__ __volatile__ (
        "amoswap.w %[pre], %[new], %[ptr]\n"
		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
		:[new]"r" (new_v)
		:"memory");
    return pre_v;
}

uint32_t amo32_add(uint32_t *ptr_v, uint32_t new_v) {
    uint32_t pre_v;
	__asm__ __volatile__ (
        "amoadd.w %[pre], %[new], %[ptr]\n"
		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
		:[new]"r" (new_v)
		:"memory");
    return pre_v;
}

uint32_t amo32_and(uint32_t *ptr_v, uint32_t new_v) {
    uint32_t pre_v;
	__asm__ __volatile__ (
        "amoand.w %[pre], %[new], %[ptr]\n"
		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
		:[new]"r" (new_v)
		:"memory");
    return pre_v;
}

uint32_t amo32_or(uint32_t *ptr_v, uint32_t new_v) {
    uint32_t pre_v;
	__asm__ __volatile__ (
        "amoor.w %[pre], %[new], %[ptr]\n"
		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
		:[new]"r" (new_v)
		:"memory");
    return pre_v;
}

uint32_t amo32_xor(uint32_t *ptr_v, uint32_t new_v) {
    uint32_t pre_v;
	__asm__ __volatile__ (
        "amoxor.w %[pre], %[new], %[ptr]\n"
		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
		:[new]"r" (new_v)
		:"memory");
    return pre_v;
}

uint32_t amo32_max(uint32_t *ptr_v, uint32_t new_v) {
    uint32_t pre_v;
	__asm__ __volatile__ (
        "amomax.w %[pre], %[new], %[ptr]\n"
		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
		:[new]"r" (new_v)
		:"memory");
    return pre_v;
}

int32_t amo32_maxu(int32_t *ptr_v, int32_t new_v) {
    int32_t pre_v;
	__asm__ __volatile__ (
        "amomaxu.w %[pre], %[new], %[ptr]\n"
		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
		:[new]"r" (new_v)
		:"memory");
    return pre_v;
}

uint32_t amo32_min(uint32_t *ptr_v, uint32_t new_v) {
    uint32_t pre_v;
	__asm__ __volatile__ (
        "amomin.w %[pre], %[new], %[ptr]\n"
		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
		:[new]"r" (new_v)
		:"memory");
    return pre_v;
}

int32_t amo32_minu(int32_t *ptr_v, int32_t new_v) {
    int32_t pre_v;
	__asm__ __volatile__ (
        "amominu.w %[pre], %[new], %[ptr]\n"
		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
		:[new]"r" (new_v)
		:"memory");
    return pre_v;
}
#if __riscv_xlen == 64
    uint64_t atomic64_fetch_add_unless(uint64_t counter, uint64_t a, uint64_t u)
    {
           uint64_t prev, rc;
    
    	__asm__ __volatile__ (
    		"0:	lr.d     %[p],  %[c]\n"
    		"	beq      %[p],  %[u], 1f\n"
    		"	add      %[rc], %[p], %[a]\n"
    		"	sc.d.rl  %[rc], %[rc], %[c]\n"
    		"	bnez     %[rc], 0b\n"
    		"	fence    rw, rw\n"
    		"1:\n"
    		: [p]"=&r" (prev), [rc]"=&r" (rc), [c]"+A" (counter)
    		: [a]"r" (a), [u]"r" (u)
    		: "memory");
    	return prev;
    }
    
    uint64_t cas64_lr_sc(uint64_t *ptr_v, uint64_t exp_v, uint64_t wr_v)
    {
           uint64_t ret_v;
    
    	__asm__ __volatile__ (
    		"0:	lr.d     %[ret],  %[ptr]\n"
    		"	bne      %[ret],  %[exp], 1f\n"
    		"	sc.d     %[ret], %[wr], %[ptr]\n"
    		"	j 2f\n"
    		"1: li %[ret], 1\n"
    		"2: \n"
    		: [ret]"=&r" (ret_v), [ptr]"+A" (*ptr_v)
    		: [wr]"r" (wr_v), [exp]"r" (exp_v)
    		: "memory");
    	return ret_v;
    }
    
    uint64_t cas64_lr_aq_sc(uint64_t *ptr_v, uint64_t exp_v, uint64_t wr_v)
    {
           uint64_t ret_v;
    
    	__asm__ __volatile__ (
    		"0:	lr.d.aq  %[ret],  %[ptr]\n"
    		"	bne      %[ret],  %[exp], 1f\n"
    		"	sc.d     %[ret], %[wr], %[ptr]\n"
    		"	j 2f\n"
    		"1: li %[ret], 1\n"
    		"2: \n"
    		: [ret]"=&r" (ret_v), [ptr]"+A" (*ptr_v)
    		: [wr]"r" (wr_v), [exp]"r" (exp_v)
    		: "memory");
    	return ret_v;
    }
    
    uint64_t cas64_lr_sc_rl(uint64_t *ptr_v, uint64_t exp_v, uint64_t wr_v)
    {
           uint64_t ret_v;
    
    	__asm__ __volatile__ (
    		"0:	lr.d     %[ret],  %[ptr]\n"
    		"	bne      %[ret],  %[exp], 1f\n"
    		"	sc.d.rl  %[ret], %[wr], %[ptr]\n"
    		"	j 2f\n"
    		"1: li %[ret], 1\n"
    		"2: \n"
    		: [ret]"=&r" (ret_v), [ptr]"+A" (*ptr_v)
    		: [wr]"r" (wr_v), [exp]"r" (exp_v)
    		: "memory");
    	return ret_v;
    }
    
    void swap64_get_lock(uint64_t *ptr_v) {
        uint64_t pre_v;
        uint64_t new_v = 1;
    	__asm__ __volatile__ (
            "0: amoswap.d.aq %[pre], %[new], %[ptr]\n" // Attempt to acquire lock.
            "   bnez %[pre], 0b\n" // Retry if held.
    		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
    		:[new]"r" (new_v)
    		:"memory");
        return;
    }
    
    void swap64_put_lock(uint64_t *ptr_v) {
    	__asm__ __volatile__ (
            "amoswap.d.rl x0, x0, %[ptr]\n"
    		:[ptr]"+A" (*ptr_v)
    		:
    		:"memory");
        return;
    }
    
    void cas64_get_lock(uint64_t *ptr_v){
        while(cas64_lr_aq_sc(ptr_v, 0, 1));
    }
    
    void cas64_put_lock(uint64_t *ptr_v){
        while(cas64_lr_sc_rl(ptr_v, 1, 0));
    }
    
    uint64_t amo64_swap(uint64_t *ptr_v, uint64_t new_v) {
        uint64_t pre_v;
    	__asm__ __volatile__ (
            "amoswap.d %[pre], %[new], %[ptr]\n"
    		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
    		:[new]"r" (new_v)
    		:"memory");
        return pre_v;
    }
    
    uint64_t amo64_add(uint64_t *ptr_v, uint64_t new_v) {
        uint64_t pre_v;
    	__asm__ __volatile__ (
            "amoadd.d %[pre], %[new], %[ptr]\n"
    		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
    		:[new]"r" (new_v)
    		:"memory");
        return pre_v;
    }
    
    uint64_t amo64_and(uint64_t *ptr_v, uint64_t new_v) {
        uint64_t pre_v;
    	__asm__ __volatile__ (
            "amoand.d %[pre], %[new], %[ptr]\n"
    		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
    		:[new]"r" (new_v)
    		:"memory");
        return pre_v;
    }
    
    uint64_t amo64_or(uint64_t *ptr_v, uint64_t new_v) {
        uint64_t pre_v;
    	__asm__ __volatile__ (
            "amoor.d %[pre], %[new], %[ptr]\n"
    		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
    		:[new]"r" (new_v)
    		:"memory");
        return pre_v;
    }
    
    uint64_t amo64_xor(uint64_t *ptr_v, uint64_t new_v) {
        uint64_t pre_v;
    	__asm__ __volatile__ (
            "amoxor.d %[pre], %[new], %[ptr]\n"
    		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
    		:[new]"r" (new_v)
    		:"memory");
        return pre_v;
    }
    
    uint64_t amo64_max(uint64_t *ptr_v, uint64_t new_v) {
        uint64_t pre_v;
    	__asm__ __volatile__ (
            "amomax.d %[pre], %[new], %[ptr]\n"
    		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
    		:[new]"r" (new_v)
    		:"memory");
        return pre_v;
    }
    
    int64_t amo64_maxu(int64_t *ptr_v, int64_t new_v) {
        int64_t pre_v;
    	__asm__ __volatile__ (
            "amomaxu.d %[pre], %[new], %[ptr]\n"
    		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
    		:[new]"r" (new_v)
    		:"memory");
        return pre_v;
    }
    
    uint64_t amo64_min(uint64_t *ptr_v, uint64_t new_v) {
        uint64_t pre_v;
    	__asm__ __volatile__ (
            "amomin.d %[pre], %[new], %[ptr]\n"
    		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
    		:[new]"r" (new_v)
    		:"memory");
        return pre_v;
    }
    
    int64_t amo64_minu(int64_t *ptr_v, int64_t new_v) {
        int64_t pre_v;
    	__asm__ __volatile__ (
            "amominu.d %[pre], %[new], %[ptr]\n"
    		:[pre]"=&r" (pre_v), [ptr]"+A" (*ptr_v)
    		:[new]"r" (new_v)
    		:"memory");
        return pre_v;
    }
#endif
#endif
