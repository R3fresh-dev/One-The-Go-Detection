#pragma once
#include <cstdint>
#include <string>
namespace otgd_reader {
// Parse only UTC API timestamps. This is syntax/duration arithmetic; it does
// not manufacture a device wall clock. Fractions retain microsecond precision.
inline bool utcMicros(const std::string& text,uint64_t& value) {
  if(text.size()<20||text.size()>27||text[4]!='-'||text[7]!='-'||text[10]!='T'||text[13]!=':'||text[16]!=':'||text.back()!='Z')return false;
  auto digits=[&](size_t at,size_t count,int& out){out=0;for(size_t i=at;i<at+count;i++){if(text[i]<'0'||text[i]>'9')return false;out=out*10+text[i]-'0';}return true;};
  int y,m,d,h,n,s;if(!digits(0,4,y)||!digits(5,2,m)||!digits(8,2,d)||!digits(11,2,h)||!digits(14,2,n)||!digits(17,2,s)||y<2020||y>2100||m<1||m>12||h>23||n>59||s>59)return false;
  static const int days[]={31,28,31,30,31,30,31,31,30,31,30,31};const int maxDay=days[m-1]+(m==2&&((y%4==0&&y%100!=0)||y%400==0));if(d<1||d>maxDay)return false;
  uint64_t fraction=0;if(text.size()!=20){if(text[19]!='.'||text.size()<22)return false;const size_t count=text.size()-21;int micros;if(count>6||!digits(20,count,micros))return false;fraction=uint64_t(micros);for(size_t i=count;i<6;i++)fraction*=10;}
  y-=m<=2;const int era=y/400;const unsigned year=unsigned(y-era*400);const unsigned doy=(153*(m+(m>2?-3:9))+2)/5+unsigned(d)-1;const unsigned doe=year*365+year/4-year/100+doy;const int64_t dayCount=int64_t(era)*146097+doe-719468;
  value=uint64_t(dayCount*86400+h*3600+n*60+s)*1000000+fraction;return true;
}
inline bool nonceWithinSignedLifetime(const char* issued,const char* expires,uint64_t nonceCreated,uint64_t received) {
  uint64_t start=0,end=0;if(!issued||!expires||!utcMicros(issued,start)||!utcMicros(expires,end)||end<=start||end-start>60000000||received<nonceCreated)return false;
  // Nonce was created before the server signature, so its elapsed age is a
  // conservative upper bound: refusing at equality cannot accept an expiry.
  const uint64_t elapsed=received-nonceCreated;return elapsed<60000 && elapsed*1000<end-start;
}
}
