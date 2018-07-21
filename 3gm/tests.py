import pytest
import pparser as parser
import syntax
import entities
import database
import pprint
import helpers
import tokenizer
import re
import phrase_fun

global db
db = database.Database()

# Law Parsing Tests
def _test_law_parsing_from_government_gazette_issue():
	issue = parser.IssueParser('../data/15.txt')
	new_laws = issue.detect_new_laws()
	for k in new_laws.keys():
		assert(new_laws[k].corpus['15'] == '1.  Η Επιτροπή Κεφαλαιαγοράς χορηγεί άδεια λειτουργίας Α.Ε.Π.Ε.Υ. μόνον εφόσον η αιτούσα εταιρεία έχει επαρκές  αρχικό κεφάλαιο, σύμφωνα με τις απαιτήσεις του Κανονισμού (ΕΕ) 575/2013, λαμβανομένης υπόψη της φύσης της σχετικής επενδυτικής υπηρεσίας ή δραστηριότητας. ')

# Entities Tests
def test_full_numbers_to_integer():
	assert(entities.Numerals.full_number_to_integer(
		'εξακοσιοστό εξηκοστό έκτο') == 666)
	assert(entities.Numerals.full_number_to_integer(
		'τετρακοσιοστός τέταρτος') == 404)

def test_greek_nums():
	x = entities.Numerals.GreekNum('ιβ')
	assert(x.value == 12)
	x.s = 'ια'
	assert(x.value == 11)

# Syntax Tests
# Phrasal operations
def test_phrase():
	import codifier

	law = codifier.codifier.laws['ν. 4511/2018']
	test =  law.sentences['1']['1']

	test1 =  phrase_fun.replace_phrase(test, 'επίδοσής της στο αντίδικο μέρος', 'foo')
	tmp = '. '.join(test1)
	assert('επίδοσής της στο αντίδικο μέρος' not in tmp and 'foo' in tmp)

	test2 =  phrase_fun.remove_phrase(test1, 'foo')
	assert('foo' not in '. '.join(test2))

	test3 = phrase_fun.insert_phrase(test1, 'appended')
	assert(test3[-1].endswith('appended'))

	test4 =  phrase_fun.insert_phrase(test1, 'prepended', position='prepend')
	assert(test4[0].startswith('prepended'))

	test5 = phrase_fun.insert_phrase(test1, 'boo', position='before', old_phrase='foo')
	tmp = '. '.join(test5)
	assert('boo foo' in tmp)

	test6 = phrase_fun.insert_phrase(test1, 'boo', position='after', old_phrase='foo')
	tmp = '. '.join(test6)
	assert('foo boo' in tmp)

	test7 = law.insert_phrase('boo', position='before', old_phrase='επίδοσής της στο αντίδικο μέρος', article='1', paragraph='1')
	assert('boo επίδοσής της στο αντίδικο μέρος' in '. '.join(test7['articles']['1']['1']))

def test_phrase_ops():
	s = 'Στην περίπτωση α΄ της παραγράφου 1 του άρθρου 12 του ν. 4067/2012, διαγράφεται η φράση «και το ισχύον ποσοστό κάλυψης»'
	q = 'Στην παράγραφο 2 του άρθρου 5 της από 24.12.1990 Πράξης Νομοθετικού Περιεχομένου «Περί Μουσουλμάνων Θρησκευτικών Λειτουργών» (Α΄182) που κυρώθηκε με το άρθρο μόνο του ν. 1920/1991 (Α΄11) μετά τη φράση «Ο Μουφτής ασκεί δικαιοδοσία» προστίθεται η φράση «, υπό τις προϋποθέσεις και τις διαδικασίες που ορίζονται στην παράγραφο 4,»'
	r =  'Στο τέλος της υποπερίπτωσης α΄ της περίπτωσης δ΄ της παραγράφου 3 του άρθρου 9 του ν. 4256/2014 (Α΄ 92) προστίθεται η ακόλουθη φράση: «και τις υποχρεώσεις για την υποβολή πληροφοριών κατάπλου και απόπλου, που απορρέουν από την ενωσιακή νομοθεσία και περιγράφονται στο π.δ. 49/2005 (Α΄ 66), όπως έχει τροποποιηθεί και ισχύει, και στο π.δ. 16/2011 (Α΄ 36).»'
	t = 'Στην παράγραφο 6 του άρθρου 51 η φράση «κατά το χρόνο που θα οριστούν τα ανωτέρω σχολεία ως» αντικαθίσταται από τη λέξη «στα νέα σχολεία»'

	tr = {'phrase': {'old_phrase': 'κατά το χρόνο που θα οριστούν τα ανωτέρω σχολεία ως', 'new_phrase': 'στα νέα σχολεία'}, 'what': {'content': 'κατά το χρόνο που θα οριστούν τα ανωτέρω σχολεία ως'}, 'root': {'action': 'αντικαθίσταται'}}
	qr = {'phrase': {'location': 'after', 'new_phrase': ', υπό τις προϋποθέσεις και τις διαδικασίες που ορίζονται στην παράγραφο 4,', 'old_phrase': 'Ο Μουφτής ασκεί δικαιοδοσία'}, 'what': {'content': ', υπό τις προϋποθέσεις και τις διαδικασίες που ορίζονται στην παράγραφο 4,'}, 'root': {'action': 'προστίθεται'}}
	rr = {'phrase': {'location': 'append', 'new_phrase': 'και τις υποχρεώσεις για την υποβολή πληροφοριών κατάπλου και απόπλου, που απορρέουν από την ενωσιακή νομοθεσία και περιγράφονται στο π.δ. 49/2005 (Α΄ 66), όπως έχει τροποποιηθεί και ισχύει, και στο π.δ. 16/2011 (Α΄ 36).', 'old_phrase': ''}, 'what': {'content': 'και τις υποχρεώσεις για την υποβολή πληροφοριών κατάπλου και απόπλου, που απορρέουν από την ενωσιακή νομοθεσία και περιγράφονται στο π.δ. 49/2005 (Α΄ 66), όπως έχει τροποποιηθεί και ισχύει, και στο π.δ. 16/2011 (Α΄ 36).'}, 'root': {'action': 'προστίθεται'}}
	sr = {'phrase': {'old_phrase': 'και το ισχύον ποσοστό κάλυψης'}, 'what': {'content': 'και το ισχύον ποσοστό κάλυψης'}, 'root': {'action': 'διαγράφεται'}}

	assert(phrase_fun.detect_phrase_components(t,  {'root' : {'action' : 'αντικαθίσταται'}, 'what' : {},  'phrase' : {}}) == tr)
	assert(phrase_fun.detect_phrase_components(q,  {'root' : {'action' : 'προστίθεται'}, 'what' : {},  'phrase' : {}}) == qr)
	assert(phrase_fun.detect_phrase_components(r,  {'root' : {'action' : 'προστίθεται'}, 'what' : {},  'phrase' : {}}) == rr)
	assert(phrase_fun.detect_phrase_components(s,  {'root' : {'action' : 'διαγράφεται'}, 'what' : {},  'phrase' : {}}) == sr)

# Tokenization test
def test_tokenizer():
	assert(tokenizer.tokenizer.split('Έλα στις 6 π.μ. και μην αργήσεις. Είναι σημαντικό') == ['Έλα στις 6 π.μ. και μην αργήσεις', ' Είναι σημαντικό'])
	assert(tokenizer.tokenizer.remove_subordinate('Κάτι, όπως έγινε, δεν είναι καλό') == 'Κάτι δεν είναι καλό')

def test_syntax_from_string():
	s = '''Στο τέλος του άρθρου 5 της από 24.12.1990 Πράξης Νομοθετικού Περιεχομένου «Περί Μουσουλμάνων Θρησκευτικών Λειτουργών» (Α΄182) που κυρώθηκε με το άρθρο μόνο του ν. 1920/1991 (Α΄11) προστίθεται παράγραφος 4 ως εξής:  «4.α. Οι υποθέσεις της παραγράφου 2 ρυθμίζονται από τις κοινές διατάξεις και μόνο κατ’ εξαίρεση υπάγονται στη δικαιοδοσία του Μουφτή, εφόσον αμφότερα τα διάδικα μέρη υποβάλουν σχετική αίτησή τους ενώπιόν του για επίλυση της συγκεκριμένης διαφοράς κατά τον Ιερό Μουσουλμανικό Νόμο. Η υπαγωγή της υπόθεσης στη δικαιοδοσία του Μουφτή είναι αμετάκλητη και αποκλείει τη δικαιοδοσία των τακτικών δικαστηρίων για τη συγκεκριμένη διαφορά. Εάν οποιοδήποτε από τα μέρη δεν επιθυμεί την υπαγωγή της υπόθεσής του στη δικαιοδοσία του Μουφτή, δύναται να προσφύγει στα πολιτικά δικαστήρια, κατά τις κοινές ουσιαστικές και δικονομικές διατάξεις, τα οποία σε κάθε περίπτωση έχουν το τεκμήριο της δικαιοδοσίας.  β. Με προεδρικό διάταγμα που εκδίδεται με πρόταση των Υπουργών Παιδείας, Έρευνας και Θρησκευμάτων και Δικαιοσύνης, Διαφάνειας και Ανθρωπίνων Δικαιωμάτων καθορίζονται όλοι οι αναγκαίοι δικονομικοί κανόνες για τη συζήτηση της υπόθεσης ενώπιον του Μουφτή και την έκδοση των αποφάσεών του και ιδίως η διαδικασία υποβολής αιτήσεως των μερών, η οποία πρέπει να περιέχει τα στοιχεία των εισαγωγικών δικογράφων κατά τον Κώδικα Πολιτικής Δικονομίας και, επί ποινή ακυρότητας, ρητή ανέκκλητη δήλωση κάθε διαδίκου περί  επιλογής της συγκεκριμένης δικαιοδοσίας, η παράσταση των πληρεξουσίων δικηγόρων, η διαδικασία κατάθεσης και επίδοσής της στο αντίδικο μέρος, η διαδικασία της συζήτησης και της έκδοσης απόφασης, τα θέματα οργάνωσης, σύστασης και διαδικασίας πλήρωσης θέσεων προσωπικού (μονίμων, ιδιωτικού δικαίου αορίστου χρόνου και μετακλητών υπαλλήλων) και λειτουργίας της σχετικής υπηρεσίας της τήρησης αρχείου, καθώς και κάθε σχετικό θέμα για την εφαρμογή του παρόντος. γ. Οι κληρονομικές σχέσεις των μελών της μουσουλμανικής μειονότητας της Θράκης ρυθμίζονται από τις διατάξεις του Αστικού Κώδικα, εκτός εάν ο διαθέτης συντάξει ενώπιον συμβολαιογράφου δήλωση τελευταίας βούλησης, κατά τον τύπο της δημόσιας διαθήκης, με αποκλειστικό περιεχόμενό της τη ρητή επιθυμία του να υπαχθεί η κληρονομική του διαδοχή στον Ιερό Μουσουλμανικό Νόμο. Η δήλωση αυτή είναι ελεύθερα ανακλητή, είτε με μεταγενέστερη αντίθετη δήλωσή του ενώπιον συμβολαιογράφου είτε με σύνταξη μεταγενέστερης διαθήκης, κατά τους όρους του Αστικού Κώδικα. Ταυτόχρονη εφαρμογή του Αστικού Κώδικα και του Ιερού Μουσουλμανικού Νόμου στην κληρονομική περιουσία ή σε ποσοστό ή και σε διακεκριμένα στοιχεία αυτής απαγορεύεται.»'''

	syntax.ActionTreeGenerator.generate_action_tree_from_string(s)
