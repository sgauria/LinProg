var x1 >=0 ;
var x2 >=0 ;
var x3 >=0 ;
var x4 >=0 ;
var x5 >=0 ;
maximize obj: 1.0  + 0.0 * x1   + 3.0 * x2 ;
c1: x3 = 1.0  + 0.0 * x1  -1.0 * x2 ;
c2: x4 = 2.0  -1.0 * x1  + 2.0 * x2 ;
c3: x5 = 1.0  -2.0 * x1  + 0.0 * x2 ;
solve; 
display 1.0  + 0.0 * x1   + 3.0 * x2 ;
 
 end; 
