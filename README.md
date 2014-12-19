Validation and Update Tool for Language Codes in MARC Records
=============================================================

Functionality
-------------
* If language codes are concatenated by subfield in the 041, separates into individual subfields while maintaining original order. Example: $a engfre $h ger $b russpa becomes $a eng $a fre $h ger $b rus $b spa. If the concatenated string is not divisible by 3, writes data to error log.
--> Separating the codes enables SolrMarc to index these values.
* Normalizes to lower case, removes any leading and trailing spaces, and deletes any trailing period from the language code string before validating.
* Checks language codes in the 008 and 041 fields against list of valid MARC language codes. If code is invalid, writes data to error log. If code is discontinued, updates to current code.
* Checks subfield codes in the 041 field against list of valid subfields for that field. If code is invalid, writes data to error log.
* At the end of processing, if updates have been made to the record and no errors have been logged, the updated record is written to a MARC output file.

Input
-----
* A file in MARC format, selected through a GUI dialog box

Output
------
* inputfilename_out.mrc: MARC file with records that were updated and validated
* inputfilename_error.txt: Main error log
* inputfilename_blank008.txt: If the error is that characters 35-37 of the 008 field are blank or '|||'
* inputfilename_log.txt: Processing statistics

Validation
----------
The following conditions will trigger an error:

* Multiple instances of 008 field in record (record will not be analyzed further).
* Multiple instances of 041 field in record (record will not be analyzed further; this is valid MARC, but not handled by the script).
* Language code (in 008 or 041) is discontinued, but does not have current equivalent.
* Language code (in 008 or 041) is not on the list of valid or discontinued codes.
* Invalid delimiter in 041 field.
* A language code that is not 3 characters in length.

Dependences
-----------
* pymarc

Credit
------
Script by Arcadia Falcone, arcadiafalcone at gmail
Updated 2014-12-19
