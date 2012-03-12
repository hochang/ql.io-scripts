"""
This script generates template for ql.io table building trading api tables only
@input sample.xml contains the xml formatted input prototype provided at http://developer.ebay.com/DevZone/XML/docs/Reference/eBay/index.html
output, xxx.ejs and xxx.ql that are located at ../tables/trading directory
where xxx is dynamically analyzied in the samlple.xml's request tag
"""
import xml.sax
class ABContentHandler(xml.sax.ContentHandler):
    def __init__(self, outfile):
        xml.sax.ContentHandler.__init__(self)
        self._tree1 = [True,True]
        self._nestlv = 0
        self.param = []
        self.last = None
        self.attrs = []
        self.oldKeep = []
        self.f = open(outfile,'w')
        self.write("""<%
var TAGNAME = 0
var CONTENT = 1
var ATTRS = 2
var ANCESTORS = 3
//check if an associative array is empty
function isaaEmpty(aa){
    for (key in aa)
        return false
    return true
}

//attrs is an associative array that holds attributes key-value pairs
function openTag(tagName, attrs){%>
    <<%= tagName %>
    <%for (attrKey in attrs){%>
        <%= attrKey %> = <%= attrs[attrKey] %>
    <%}%>
    >
<%}

function closeTag(tagName){%>
    </<%=tagName%>>
<%}

function insert(value){%>
    <%= value %>
<%}

function printAncestors(ancestorTags){
    if (! (ancestorTags instanceof Array))
        return
    for (var i = 0; i < ancestorTags.length; i++)
        openTag(ancestorTags[i])
}



function tagNode(tagName, value, attrs){
var tmp =
{
'tagName' : tagName,
'attrs' : attrs,
'isEmpty' : false,
'print' : function(){
    if(this.isEmpty)
        return
    for (var i = 0; i < this.value.length; i++){%>
        <<%=tagName%>><%= this.value[i] %></<%=tagName%>>
    <%}
}
}
//take either one or array of values
if (value instanceof Array)
    tmp.value = value
else{
    tmp.value = [value]
    if (value == null && isaaEmpty(attrs))
        tmp.isEmpty = true
}

return tmp
}

function printTagNode(tagName, value, attrs){
    var tmp = tagNode(tagName, value, attrs)
    tmp.print()
}

function tagTree(tagName, children, attrs){
var tmp = {
'tagName' : tagName,
'attrs' : attrs,
'print' : function(){
    if(this.isEmpty)
        return
    for(var childIdx = 0; childIdx < this.children.length; childIdx++){
        openTag(this.tagName)

        var child = this.children[childIdx]
        for (var childTag =0; childTag <child.length; childTag++){
            child[childTag].print()
        }
        closeTag(this.tagName)
    }
}
}
if (!(children[0] instanceof Array))
    tmp.children = [children]
else
    tmp.children = children
tmp.isEmpty = true
for (var childIdx = 0; childIdx < tmp.children.length; childIdx++){
    var child = tmp.children[childIdx]
    for (var childTag =0; childTag <child.length; childTag++){
        if (!(child[childTag].isEmpty)){
            tmp.isEmpty = false
            break
        }
    }if(!tmp.isEmpty)
        break
}
return tmp
}

function printTagTree(tagName, children, attrs){
    var tmp = tagTree(tagName, children, attrs)
    tmp.print()
}
%>

<?xml version="1.0" encoding="utf-8"?>
""",0)
    def write(self, txt, indent):
        self.f.write('\n'+' '*4*indent+txt)

    def startElement(self, name, attrs):
        self._nestlv += 1
        if self._nestlv == 1:
            self.f.write('<'+name+""" xmlns="urn:ebay:apis:eBLBaseComponents"><%
    printTagTree('RequesterCredentials', [tagNode('eBayAuthToken', params['RequesterCredentials.eBayAuthToken'])])""")
            self.oldKeep.append(False)
            return


        if self._nestlv == 3:# previous tag is a tree
            if self._tree1[-1]:
                self.write("printTagTree('"+self.param[-1]+"', [", self._nestlv-2)
            #self._tree1 = True
        elif self._nestlv > 3:
            if self._tree1[-1]:
                if not self._tree1[-2]:
                    self.f.write(',')
                self._tree1[-2] = False
                self.write("tagTree('"+self.param[-1]+"', [", self._nestlv-2)
                #self._tree1[-1] = False

        #self._tree1[-1] = False
        self._tree1.append(True)



        self.param.append(name)
        self.last = name
        s="startElement '" + name + "'"
        #self.write(s)
        new_attrs = []
        for key in attrs.keys():
            #print "<"+name+" "+key+"="+attrs.get(key)+">"
            key_str = str(key)
            new_attrs.append(key_str)
        self.attrs.append(new_attrs)
        #print self.attrs
        #if name == "address":
        #    print("\tattribute type='" + attrs.getValue("type") + "'")
        #print 'open ',name,self._tree1

    def getParam(self):
        s = '.'.join(self.param)
        if len(self.param) > 1:
            return "params['"+s+"']"
        else:
            return 'params.'+s

    def getAttr(self, attr):
        s ='.'.join(self.param)
        s+'.'+attr
        return "params['"+s+"']"

    def endElement(self, name):
        self._tree1.pop()
        self._nestlv -= 1
        if self._nestlv == 0:
            self.write('%></'+name+'>',self._nestlv)
            return


        if name == self.last:# this is a tagNode, nodes are not closed
            if self._nestlv == 1:
                self.write("printTagNode('"+name+"', "+self.getParam(), self._nestlv)
            else:
                if not self._tree1[-1]:
                    self.f.write(', ')
                else:
                    self._tree1[-1] = False
                self.write("tagNode('"+name+"', "+self.getParam(), self._nestlv)
        else:
            self.f.write(']')
        #else:
        #self._tree1[-1] = False
        old_attr = self.attrs.pop()
        if len(old_attr):
            self.f.write(', {')
            for attr in old_attr:
                #attr_str=str(attr)
                if attr != old_attr[0]:
                    self.f.write(', ')
                self.write(attr+' : '+self.getAttr(attr), self._nestlv)
            self.f.write('}')
        #else:
        #    self.f.write('\n')
        #self.write(self.getParam())
        self.f.write(')')
        giveup = self.param.pop()
        if giveup != name:
            raise NameError('HiThere')
        s="endElement '" + name + "'"
        #print 'close',name,self._tree1

    def characters(self, content):
        pass
        #print("characters '" + content + "'")

    def endDocument(self):
        self.f.close()

def makeQL(opname, env):
    s = """-- Example: select * from ebay.trading.GetBestOffers
--
create table ebay.trading.GetBestOffers
  on select post to "{config.tables.ebay.trading.production.gateway}"
     using headers 'X-EBAY-API-COMPATIBILITY-LEVEL' = '{config.tables.ebay.trading.version}',
                   'X-EBAY-API-SITEID' = '{config.tables.ebay.trading.siteid}',
                   'X-EBAY-API-CALL-NAME'= 'GetBestOffers'
      using defaults RequesterCredentials.eBayAuthToken = '{config.tables.ebay.trading.production.eBayAuthToken}'
      using bodyTemplate 'GetBestOffers.ejs' type 'application/xml'
      resultset 'GetBestOffersResponse'"""
    s= s.replace("GetBestOffers", opname)
    s= s.replace("config.tables.ebay.trading.production", env)
    f = open('../tables/trading/'+opname+'.ql','w')
    f.write(s)
    f.close()

def main(sourceFileName):#, outputFileName):
    source = open(sourceFileName)
    another = open(sourceFileName, 'r')
    opname = another.readlines()[-1][2:-8]
    print opname, 'o yeah~'
    another.close()
    newfname = '../tables/trading/'+opname+'.ejs'
    xml.sax.parse(source, ABContentHandler(newfname))

    makeQL(opname, "config.tables.ebay.trading.sandbox")

if __name__ == "__main__":
    main("sample.xml")#,"output.ejs")