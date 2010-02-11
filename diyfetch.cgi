#!/usr/bin/perl

use strict;
use CGI qw/:standard/;;
use CGI::Carp qw(fatalsToBrowser);
require LWP::UserAgent;
use XML::Simple;
use Data::Dumper;

my $ua = LWP::UserAgent->new;
$ua->timeout(10);

my $id = param('id') || die "no feed id specified"; 
die "bad id" if $id !~ m/^\d+$/;     # block unsafe chars
my $url = "http://www.diynetwork.com/diy/channel/xml/0,,$id,00.xml";
my $response = $ua->get($url);

if (!$response->is_success) {
    die $response->status_line;
}


my $xml = $response->content;
$xml =~ s/^[\r\n\s]+(<\?xml)/$1/s;   # remove stray linebreaks that break XML parsing.
my $ref = XMLin($xml) || die "failed to parse xml feed";


print header(-type => 'text/xml', -charset => 'utf-8');

print <<DOCEND;
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:boxee="http://boxee.tv/spec/rss/">
<channel>
   <title>$ref->{title}</title>
   <link>http://boxee.bovine.net/</link>
   <description>$ref->{title}</description>
   <language>en-us</language>
   <boxee:display>
     <boxee:sort default="1" folder-position="start">
       <boxee:sort-option id="1" sort-by="default" sort-type-name="default"/>
       <boxee:sort-option id="2" sort-by="label" sort-type-name="Title" sort-order="ascending"/>
     </boxee:sort>
   </boxee:display>
DOCEND


foreach my $video (@{$ref->{video}}) {
    #print Dumper(\$video);
    die "expecting wmv type" if $video->{'videoUrl'} !~ m/\.wmv$/;

    # TODO: escape unsafe chars as XML entities
    print <<DOCEND;
    <item>
    <title>$video->{'clipName'}</title>
    <description>$video->{'abstract'}</description>
    <guid>$video->{'videoUrl'}</guid>
    <media:content url="$video->{'videoUrl'}" type="video/x-ms-wvx" />
    <media:thumbnail url="$video->{'thumbnailUrl'}" width="480" height="360" />
    <media:category scheme="urn:boxee:show-title">$ref->{title}</media:category>
    <media:category scheme="urn:boxee:title-type">tv</media:category>
    <boxee:tv-show-title>$ref->{title}</boxee:tv-show-title>
    <boxee:provider-name>DIY Network</boxee:provider-name>
    <boxee:provider-thumb>http://boxee.bovine.net/diylogo.jpg</boxee:provider-thumb>
    <boxee:runtime>$video->{'length'}</boxee:runtime>
    </item>
DOCEND


}
print "</channel>\n";
print "</rss>\n";
exit 0;
