from pymarc import *
from datetime import datetime

## Script by Arcadia Falcone, arcadia.falcone at gmail.com, updated 12/19/2014
## Validates and updates language codes in MARC records:
## -Checks language codes in 008 and 041 against valid MARC language codes
## -If code in 008 or 041 is discontinued, updates to current code
## -Checks that subfield codes in 041 are valid
## -If multiple language codes are concatenated, separates each into its own 
##  instance of the subfield, maintaining the original order

def openFilesIO():
    """Select input file, and create updated MARC file and error log text file
    for output, with file names based on the input file selected."""
    import os
    import Tkinter, tkFileDialog
    root = Tkinter.Tk()
    root.withdraw()
    fileselect = tkFileDialog.askopenfilename()
    filepath = os.path.dirname(fileselect)
    filename = os.path.basename(fileselect)
    basename = os.path.splitext(filename)[0]
    in_file = os.path.abspath(fileselect)
    out_file_base = filepath + '/' + basename
    out_file = out_file_base + '_out.mrc'
    o = open(out_file, 'w')
    o.close()
    error_file = out_file_base + '_error.txt'
    log_file = out_file_base + '_log.txt'
    blank_file = out_file_base + '_blank008.txt'
    return in_file, out_file, error_file, log_file, blank_file

def repeatFieldTest(my_record, my_field_tag):
    """Test if field occurs more than once in record."""
    field_list = my_record.get_fields(my_field_tag)
    if len(field_list) > 1:
        return True

def getSubfieldsInOrder(my_field):
    """Extract subfield delimiter/value pairs from field as nested list, 
    preserving the order in which they appear in the original record.
    E.g.: subfield_pairs = [ ['a', 'eng'], ['b', 'rusfre'] ]"""
    field_string = str(my_field)[9:]
    subfield_list = field_string.split('$')
    subfield_pairs = [[0, 0] for x in range(len(subfield_list))]
    for i in range(len(subfield_list)):
        sub_string = subfield_list[i]
        subfield_pairs[i][0] = sub_string[:1]
        subfield_pairs[i][1] = sub_string[1:]
    return subfield_pairs

def writeError(error_type, field_tag, error_value, *fh):
    """Write record ID and error data to error log file. Optional fh argument 
    indicates filehandle to write to if other than default error log.
    Used in this script to write null 008 errors to separate log."""
    if fh:
        log_file = fh[0]
    else:
        log_file = error_log
        global error_log_count
        error_log_count += 1
    output = [record_id, field_tag, errors[error_type], error_value]
    line_out = '\t'.join(output) + '\n'
    log_file.write(line_out)


### Variables ###

# Discontinued codes and their replacements; oldcode:newcode
codedict = {'cam':'khm', 'esp':'epo', 'eth':'gez', 'far':'fao', 'fri':'fry', 
'gae':'gla', 'gag':'glg', 'gal':'orm', 'gua':'grn', 'int':'ina', 'iri':'gle', 
'kus':'kos', 'lan':'oci', 'lap':'smi', 'max':'glv', 'mla':'mlg', 'mol':'rum', 
'sao':'smo', 'scc':'srp', 'scr':'hrv', 'sho':'sna', 'snh':'sin', 'sso':'sot', 
'swz':'ssw', 'tag':'tgl', 'taj':'tgk', 'tar':'tat', 'tsw':'tsn'}

# Valid subfields for 041 according to MARC documentation
subfields041 = ['a', 'b', 'd', 'e', 'f', 'g', 'h', 'j', 'k', 'm', 'n']

# Valid MARC language codes
lang_codes = ['aar', 'abk', 'ace', 'ach', 'ada', 'ady', 'afa', 'afh', 'afr', 
'ain', 'aka', 'akk', 'alb', 'ale', 'alg', 'alt', 'amh', 'ang', 'anp', 'apa', 
'ara', 'arc', 'arg', 'arm', 'arn', 'arp', 'art', 'arw', 'asm', 'ast', 'ath', 
'aus', 'ava', 'ave', 'awa', 'aym', 'aze', 'bad', 'bai', 'bak', 'bal', 'bam', 
'ban', 'baq', 'bas', 'bat', 'bej', 'bel', 'bem', 'ben', 'ber', 'bho', 'bih', 
'bik', 'bin', 'bis', 'bla', 'bnt', 'bos', 'bra', 'bre', 'btk', 'bua', 'bug', 
'bul', 'bur', 'byn', 'cad', 'cai', 'car', 'cat', 'cau', 'ceb', 'cel', 'cha', 
'chb', 'che', 'chg', 'chi', 'chk', 'chm', 'chn', 'cho', 'chp', 'chr', 'chu', 
'chv', 'chy', 'cmc', 'cop', 'cor', 'cos', 'cpe', 'cpf', 'cpp', 'cre', 'crh', 
'crp', 'csb', 'cus', 'cze', 'dak', 'dan', 'dar', 'day', 'del', 'den', 'dgr', 
'din', 'div', 'doi', 'dra', 'dsb', 'dua', 'dum', 'dut', 'dyu', 'dzo', 'efi', 
'egy', 'eka', 'elx', 'eng', 'enm', 'epo', 'est', 'ewe', 'ewo', 'fan', 'fao', 
'fat', 'fij', 'fil', 'fin', 'fiu', 'fon', 'fre', 'frm', 'fro', 'frr', 'frs', 
'fry', 'ful', 'fur', 'gaa', 'gay', 'gba', 'gem', 'geo', 'ger', 'gez', 'gil', 
'gla', 'gle', 'glg', 'glv', 'gmh', 'goh', 'gon', 'gor', 'got', 'grb', 'grc', 
'gre', 'grn', 'gsw', 'guj', 'gwi', 'hai', 'hat', 'hau', 'haw', 'heb', 'her', 
'hil', 'him', 'hin', 'hit', 'hmn', 'hmo', 'hrv', 'hsb', 'hun', 'hup', 'iba', 
'ibo', 'ice', 'ido', 'iii', 'ijo', 'iku', 'ile', 'ilo', 'ina', 'inc', 'ind', 
'ine', 'inh', 'ipk', 'ira', 'iro', 'ita', 'jav', 'jbo', 'jpn', 'jpr', 'jrb', 
'kaa', 'kab', 'kac', 'kal', 'kam', 'kan', 'kar', 'kas', 'kau', 'kaw', 'kaz', 
'kbd', 'kha', 'khi', 'khm', 'kho', 'kik', 'kin', 'kir', 'kmb', 'kok', 'kom', 
'kon', 'kor', 'kos', 'kpe', 'krc', 'krl', 'kro', 'kru', 'kua', 'kum', 'kur', 
'kut', 'lad', 'lah', 'lam', 'lao', 'lat', 'lav', 'lez', 'lim', 'lin', 'lit', 
'lol', 'loz', 'ltz', 'lua', 'lub', 'lug', 'lui', 'lun', 'luo', 'lus', 'mac', 
'mad', 'mag', 'mah', 'mai', 'mak', 'mal', 'man', 'mao', 'map', 'mar', 'mas', 
'may', 'mdf', 'mdr', 'men', 'mga', 'mic', 'min', 'mis', 'mkh', 'mlg', 'mlt', 
'mnc', 'mni', 'mno', 'moh', 'mon', 'mos', 'mul', 'mun', 'mus', 'mwl', 'mwr', 
'myn', 'myv', 'nah', 'nai', 'nap', 'nau', 'nav', 'nbl', 'nde', 'ndo', 'nds', 
'nep', 'new', 'nia', 'nic', 'niu', 'nno', 'nob', 'nog', 'non', 'nor', 'nqo', 
'nso', 'nub', 'nwc', 'nya', 'nym', 'nyn', 'nyo', 'nzi', 'oci', 'oji', 'ori', 
'orm', 'osa', 'oss', 'ota', 'oto', 'paa', 'pag', 'pal', 'pam', 'pan', 'pap', 
'pau', 'peo', 'per', 'phi', 'phn', 'pli', 'pol', 'pon', 'por', 'pra', 'pro', 
'pus', 'que', 'raj', 'rap', 'rar', 'roa', 'roh', 'rom', 'rum', 'run', 'rup', 
'rus', 'sad', 'sag', 'sah', 'sai', 'sal', 'sam', 'san', 'sas', 'sat', 'scn', 
'sco', 'sel', 'sem', 'sga', 'sgn', 'shn', 'sid', 'sin', 'sio', 'sit', 'sla', 
'slo', 'slv', 'sma', 'sme', 'smi', 'smj', 'smn', 'smo', 'sms', 'sna', 'snd', 
'snk', 'sog', 'som', 'son', 'sot', 'spa', 'srd', 'srn', 'srp', 'srr', 'ssa', 
'ssw', 'suk', 'sun', 'sus', 'sux', 'swa', 'swe', 'syc', 'syr', 'tah', 'tai', 
'tam', 'tat', 'tel', 'tem', 'ter', 'tet', 'tgk', 'tgl', 'tha', 'tib', 'tig', 
'tir', 'tiv', 'tkl', 'tlh', 'tli', 'tmh', 'tog', 'ton', 'tpi', 'tsi', 'tsn', 
'tso', 'tuk', 'tum', 'tup', 'tur', 'tut', 'tvl', 'twi', 'tyv', 'udm', 'uga', 
'uig', 'ukr', 'umb', 'und', 'urd', 'uzb', 'vai', 'ven', 'vie', 'vol', 'vot', 
'wak', 'wal', 'war', 'was', 'wel', 'wen', 'wln', 'wol', 'xal', 'xho', 'yao', 
'yap', 'yid', 'yor', 'ypk', 'zap', 'zbl', 'zen', 'zha', 'znd', 'zul', 'zun', 
'zxx', 'zza']

# Discontinued MARC language codes without one-to-one replacement (not in 
# codedict)
lang_codes_disc = ['esk']

# Define errors
errors = {
            'multiple': 'Multiple instances of field in record', 
            'updatefail': 'Code cannot be updated',
            'invalidsub': 'Invalid subfield delimiter',
            'invalidcode': 'Invalid language code',
            'not3char': 'Non-3-letter code',
            'blank': 'Blank code'
}

### Process ###

# Record start time
start_time = datetime.now()

# Select input and create output files
records_in, records_out, error, process, blank = openFilesIO()

print 'Processing %s...' % records_in

# Open .mrc files and error log file
reader = MARCReader(file(records_in, 'r'), to_unicode=True)
writer = MARCWriter(file(records_out, 'w'))
error_log = open(error, 'w')
process_log = open(process, 'w')
blank_log = open(blank, 'w')

headers = ['record_id', 'field_tag', 'error_type', 'error_value']
error_log.write('\t'.join(headers) + '\n')
blank_log.write('\t'.join(headers) + '\n')

record_in_count = 0
record_out_count = 0
record_error_count = 0
blank_008_count = 0
error_log_count = 0

for record in reader:
    record_in_count += 1

# Set current record_id and flags
    record_id = record['001'].value()
    set_error = False
    set_update = False

# Test for multiple instances of 008 or 041 field
# If either is true, write to error log and go on to next record
    if record['008'] and repeatFieldTest(record, '008') == True:
        writeError('multiple', '008', '')
        record_error_count += 1
        continue
    if record['041'] and repeatFieldTest(record, '041') == True:
        writeError('multiple', '041', '')
        record_error_count += 1
        continue

# 008
# Assign 008 language code to variable
    lang_008 = record['008'].value()[35:38]
# Trim leading and trailing spaces
    lang_008 = lang_008.strip()
# Check for blank/null
    if lang_008 == '' or lang_008 == '|||':
        writeError('blank', '008', lang_008, blank_log)
        blank_008_count += 1
        set_error = True
# Replace old code with new in 008 field
    elif lang_008 in codedict.keys():
        new008 = record['008'].value()[:35] + codedict[lang_008] + record['008'].value()[38:]
        record['008'].data = new008
        set_update = True
# Test for discontinued code without replacement and write to error log if true
    elif lang_008 in lang_codes_disc:
        writeError('updatefail', '008', lang_008)
        set_error = True
# Test for invalid code and write to error log if true
    elif lang_008 not in lang_codes:
        writeError('invalidcode', '008', lang_008)
        set_error = True

# 041
    if record['041']:
# Create new empty 041 field
        new041 = Field(
            tag = '041',
            indicators = ['0', '0'],
            subfields = []
        )
# Get existing subfield delimiter-value pairs
        new_sub_pairs = []
        subfield_pairs = getSubfieldsInOrder(record['041'])
        for pair in subfield_pairs:
            sub = pair[0]
            value = pair[1]
# Test for delimiters not in subfields041 list and write to error log if true
            if sub not in subfields041:
                writeError('invalidsub', '041', sub)
                set_error = True
# Trim leading and trailing spaces
            value = value.strip()
# Delete final period
            value = value.rstrip('.')
# Test for extra characters in value and write to error log if true
            if len(value) % 3 != 0:
                writeError('not3char', '041', value)
                set_error = True
                continue
# If length of language code string is greater than 3, set update to True
            if len(value) > 3:
                set_update = True
# Change upper case to lower case
            if value != value.lower():
                value = value.lower()
                set_update = True
# Break value string into 3-letter codes
            for n in range(0, len(value)-2, 3):
                code = value[n:n+3]
# Replace old code with new and add updated subfield to new 041 field
                if code in codedict.keys():
                    newcode = codedict[code]
                    new041.add_subfield(sub, newcode)
                    set_update = True
# Test for discontinued code without replacement and write to error log if true
                elif code in lang_codes_disc:
                    writeError('updatefail', '041', code)
                    set_error = True
# Test for invalid code and write to error log if true
                elif code not in lang_codes:
                    writeError('invalidcode', '041', code)
                    set_error = True
# Add existing valid subfield to new 041 field
                else:
                    new041.add_subfield(sub, code)
# Replace old 041 field values with new in record
        record['041'].subfields = new041.subfields

# Write to output .mrc file
    if set_error == False and set_update == True:
        writer.write(record)
        record_out_count += 1
    elif set_error == True:
        record_error_count += 1

# Write summary of results to process log
stop_time = datetime.now()
process_log.write('Process started: %s' % start_time + '\n')
process_log.write('Process completed: %s' % stop_time + '\n\n')
process_log.write('%d records processed.' % record_in_count + '\n')
process_log.write('%d records updated.' % record_out_count + '\n')
process_log.write('%d records with errors.' % record_error_count + '\n')
process_log.write('%d records with null 008 language code.' % blank_008_count + '\n')
process_log.write('%d errors logged for manual review.' % error_log_count + '\n')

# Write summary of results to console
print "%d records processed." % (record_in_count)
print "%d records updated." % (record_out_count)
print "%d records with errors, including:" % (record_error_count)
print "   %d records with null 008." % (blank_008_count)
print "   %d records for manual review." % (error_log_count)

# Close files
writer.close()
error_log.close()
process_log.close()
blank_log.close()
