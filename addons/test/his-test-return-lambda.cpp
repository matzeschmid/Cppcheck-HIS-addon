// Test code for number of return points within functions
// calling an embedded lambda function.

#include <algorithm>

// The lambda function of this test code is part of dump file.
bool hasMember()
{
    return (std::any_of(memberList.cbegin(), memberList.cend(), [](MemberTag tag) { return (tag != MemberTag::NoMember); } ));
}

// The lambda function of this test code is not part of dump file up to now.
bool hasMember_MissingLambdaInDump() // HIS-RETURN
{
    bool retVal = false;
    if (std::any_of(memberList.cbegin(), memberList.cend(), [](MemberTag tag) { return (tag != MemberTag::NoMember); } ))
    {
        retVal = true;
    }
    return retVal;
}