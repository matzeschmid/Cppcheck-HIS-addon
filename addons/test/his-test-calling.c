// HIS-COMF
// Additional test code to check CALLING metric using multiple files.

#include <stdio.h>

void func_calling1() // HIS-CALLING HIS-NRECUR
{
    int idx = 1;
    (void)printf("Calling his_goto(%d)\n", idx);
    his_goto(idx);
    (void)printf("Called his_goto(%d)\n", idx);
}

void func_calling2()
{
    int idx = 2;
    (void)printf("Calling his_goto(%d)\n", idx);
    his_goto(idx);
    (void)printf("Calling his_goto(%d)\n", idx);
    his_goto(idx);
}

void func_calling3()
{
    int idx = 3;
    (void)printf("Calling his_goto(%d)\n", idx);
    his_goto(idx);  
}

void func_calling4()
{
    int idx = 4;
    (void)printf("Calling his_goto(%d)\n", idx);
    his_goto(idx);
}
