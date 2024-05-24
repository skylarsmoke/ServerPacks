<?php
/** PHP script that creates an unlock file for the Tracktion Marketplace Status. */
/** Variables */
$PRODUCT_ID = "SynergyBass";
$EMAIL = "client@rumorvst.ai";
$USER = "testuser";
$DATE = date("j M Y g:i:sa");
$MACHINE = "BYPASS";
$TIME = dec2hex(round(microtime(true)*1000));

$PRIVATE_KEY_PART_1 = "279808e40cef4350640026c8739e7201826d002cec7e260f3d16d0cf786842f1"; 
$PRIVATE_KEY_PART_2 = "602815978d207ee7ce4982c23d5c39729da90af57b850863165936256e3b7227";

header('Content-Description: File Transfer');
header('Content-Type: text/plain');
header('Content-Disposition: attachment; filename='.$PRODUCT_ID.'.licence');
header('Content-Transfer-Encoding: UTF-8');
header('Expires: 0');
        
/** Helper Functions */
function dec2hex($number)
{
    $hexvalues = array('0','1','2','3','4','5','6','7',
               '8','9','a','b','c','d','e','f');
    $hexval = '';
     while($number != '0')
     {
        $hexval = $hexvalues[bcmod($number,'16')].$hexval;
        $number = bcdiv($number,'16',0);
    }
    return $hexval;
}

include ('Math/BigInteger.php');  // get this from: phpseclib.sourceforge.net
function applyToValue ($message, $key_part1, $key_part2)
{
    $result = new Math_BigInteger();
    $zero  = new Math_BigInteger();
    $value = new Math_BigInteger (strrev ($message), 256);
    $part1 = new Math_BigInteger ($key_part1, 16);
    $part2 = new Math_BigInteger ($key_part2, 16);
    while (! $value->equals ($zero))
    {
        $result = $result->multiply ($part2);
        list ($value, $remainder) = $value->divide ($part2);
        $result = $result->add ($remainder->modPow ($part1, $part2));
    }
    return $result->toHex();
}

// Create the comment section
echo "Keyfile for ", $PRODUCT_ID, "\n";
echo "User: ", $USER, "\n";
echo "Email: ", $EMAIL, "\n";
echo "Machine numbers: ", "\n";
echo "Created: ", $DATE, "\n";
echo "\n";
// Create the XML 
$dom = new DOMDocument("1.0", "utf-8");
$root = $dom->createElement("key");
$dom->appendChild($root);
$root->setAttribute("user", $USER);
$root->setAttribute("email", $EMAIL);
$root->setAttribute("mach", $MACHINE);
$root->setAttribute("app", $PRODUCT_ID);
$root->setAttribute("date", $TIME);
$XML_STRING = $dom->saveXML();
$ENCRYPTED_XML = "#" . applyToValue($XML_STRING, $PRIVATE_KEY_PART_1, $PRIVATE_KEY_PART_2);
$XML_DATA = chunk_split($ENCRYPTED_XML, 70);
echo $XML_DATA;
?>

This is the TracktionMarketplaceStatus subclass:

 


class Unlocker: public TracktionMarketplaceStatus
{
public:
    Unlocker():
        state(String::empty)
    {}
    String getMarketplaceProductID()
    {
        return PRODUCT_ID;
    }
    RSAKey getPublicKey() override
    {
        return RSAKey(PUBLIC_KEY);
    }
    String getState() override
    {
        return state;
    };
    StringArray getLocalMachineIDs() override
    {
        StringArray sa;
        sa.add("BYPASS");
        return sa;
    };
    void saveState(const String &s) override
    {
        state = s;
    }
private:
    String state;
};