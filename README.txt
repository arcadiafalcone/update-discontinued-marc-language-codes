## README for update_discontinued_marc_language_codes_git.py
## Script by Arcadia Falcone, arcadiafalcone at gmail
## Updated 2014-07-18


# Purpose of script

Given a MARC record file (.mrc), update discontinued language codes in the 008 and 041 fields to their current equivalents, maintaining the original 041 subfield order. Also separates concatenated code strings into separate subfields (e.g., $a engfre becomes $a eng $a fre), and changes codes in upper case to lower case.


# Input

A file in MARC format (input.mrc).


# Output

output.mrc: MARC file containing updated records only.

error_log.txt: text file listing validation errors.


# Validation

Each of the following conditions will trigger an error:

1. Multiple instances of 008 field in record (record will not be analyzed further).

2. Multiple instances of 041 field in record (record will not be analyzed further; this is valid MARC, but not handled by the script).

3. Language code (in 008 or 041) is discontinued, but does not have current equivalent.

4. Language code (in 008 or 041) is not on the list of valid or discontinued codes.

5. Invalid delimiter in 041 field.

6. A language code that is not 3 characters in length.

Each error is written to the error log, and the record is not included in the MARC output.
