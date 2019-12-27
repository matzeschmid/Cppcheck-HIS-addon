// HIS-COMF
// Additional test code to check CALLING metric using multiple files.

#include <stdio.h>

void func_calling1()
{
    his_goto(1);
    (void)printf("Calling his_goto(1)\n");
}

void func_calling2()
{
    his_goto(2);
    (void)printf("Calling his_goto(2)\n");
    his_goto(2);
    (void)printf("Calling his_goto(2)\n");
}

void func_calling3()
{
    his_goto(3);
    (void)printf("Calling his_goto(3)\n");
}

void func_calling4()
{
    his_goto(4);
    (void)printf("Calling his_goto(4)\n");
}
