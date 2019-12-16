// HIS-COMF
/*
 * To test:
 * ~/cppcheck/cppcheck --dump his-test.c && python ../his.py -verify his-test.c.dump
 */

// Test pattern HIS metric - Number of goto statements: 0
void his_goto(int param)
{
    if (param < 0) {
        goto invalid_param; // HIS-GOTO 
    }
    (void)printf("Param: %d", param)
invalid_param:
    return;
}

// Test pattern HIS metric - Number of statements per function: 1-50
void his_stm_num_fail(int count)    // HIS-STMT HIS-STCYC
{
    int val = 0;
    if (count > 0) {
        (void)printf("count: %d\n", count);
        (void)printf("val:   %d\n", val);
        for (int i=0; i<count; i++) {
            val += i;
            (void)printf("val:   %d\n", val);
        }

        switch (val)
        {
            case 0:
                (void)printf("VAL 0\n");
            break;
            case 1:
                (void)printf("VAL 1\n");
            break;
            case 2:
                (void)printf("VAL 2\n");
            break;
            case 3:
                (void)printf("VAL 4\n");
            break;
            case 4:
                (void)printf("VAL 4\n");
            break;
            case 5:
                (void)printf("VAL 5\n");
            break;
            case 6:
                (void)printf("VAL 6\n");
            break;
            case 7:
                (void)printf("VAL 7\n");
            break;
            case 8:
                (void)printf("VAL 8\n");
            break;
            case 9:
                (void)printf("VAL 9\n");
            break;
            case 10:
                (void)printf("VAL 10\n");
            break;
            case 100:
                (void)printf("VAL 100\n");
            break;
            default:
                (void)printf("VAL default\n");
                his_return_none_pass();
            break;
        }
    }
    else {
        (void)printf("count: %d\n", count);
        (void)printf("Invalid count value\n");
        his_return_none_pass();
    }

    return val;
}

// Test pattern HIS metric - Number of function parameters: 0-5
void his_param_num_pass(int p1, int p2, int p3, int p4, int p5)
{
    (void)p1;
    (void)p2;
    (void)p3;
    (void)p4;
    (void)p5;
}

void his_param_num_fail(int p1, int p2, int p3, int p4, int p5, int p6)    // HIS-PARAM
{
    (void)p1;
    (void)p2;
    (void)p3;
    (void)p4;
    (void)p5;
    (void)p6;
}

// Test pattern HIS metric - Number of return points within a function: 0-1
void his_return_none_pass() // HIS-CALLING
{
}

int his_return_single_pass(int a, int b)
{
    return a + b;
}

int his_return_multiple_fail(int a, int b)  // HIS-RETURN
{
    if (a > b) {
        return a - b;
    }
    else {
        return b - a;
    }    
}

// Test pattern HIS metric - Number of called functions excluding duplicates: 0-7
void his_calls_pass()
{
    his_return_none_pass();
    his_return_single_pass(1, 2);
    his_return_multiple_fail(4, 2);
    his_return_none_pass();
    (void)printf("Hello");
    his_param_num_pass(1,2,3,4,5);
    his_param_num_fail(1,2,3,4,5,6);
    (void)printf("World");
    his_goto(0);
}

void his_calls_fail()   // HIS-CALLS
{
    his_return_none_pass();
    his_return_single_pass(1, 2);
    his_return_multiple_fail(4, 2);
    his_return_none_pass();
    (void)printf("Hello");
    his_param_num_pass(1,2,3,4,5);
    his_param_num_fail(1,2,3,4,5,6);
    (void)printf("World");
    his_goto(0);
    his_calls_pass()
}

// Test pattern HIS metric - Depth of nesting of a function: 0-4
void his_level(int x, int y, int z)	// HIS-PATH
{
    if ((x > 0) && (y > 0) && (z > 0)) {
        for (int i=0; i<x; i++) {
            int j = y;
            while (j > 0) {
                k = z;
                do {   // HIS-LEVEL
                    (void)printf("i=%d, j=%d, k=%d\n", i,j,k);
                    k--;
                } while (k > 0);
                j--;

                switch (i)  // HIS-LEVEL
                {
                    case 0:
                        (void)printf("i is zero\n");
                    break;
                    default:
                        (void)printf("i is greater than zero\n");
                    break;
                }
            }
        }
    }
    else if (x <= 0) {
        (void)printf("x is less than 1\n");
    }
    else if (y <= 0) {
        (void)printf("y is less than 1\n");
    }
    else if (z <= 0) {   // HIS-LEVEL
        (void)printf("z is less than 1\n");
    }
}
