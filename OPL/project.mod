 // A
 int numNurses = ...;
 int hours = ...;
 range N = 1..numNurses;
 range H = 1..hours;
 
 int demand [h in H]= ...;
 int minHours = ...;
 int maxHours = ...;
 int maxConsec = ...;
 
 // B
 int maxPresence = ...;
 int maxIndex = ftoi(floor((maxConsec+1)/2));
 int minIndex = maxIndex - maxConsec;
 
 range Index = minIndex..maxIndex;
 
 //C
 range restIndex= 0..1;

 // A
 dvar boolean works[n in N][h in H]; // this set of variable should suffice for A). Tells whether nurse n works at hour h
 dvar boolean worksBefore[n in N][h in H];
 dvar boolean worksAfter[n in N][h in H];
 
minimize sum(n in N) ((sum(h in H) works[n, h] >= 1) + (sum(h in H) works[n, h]));

 subject to {
  
  /* The total demand for an specified hour should be fulfilled*/
 	forall(h in H)
 	  sum(n in N) works[n, h] >= demand[h];
 	
 /* All nurses, if they work, the should work at least minHours hours */		
 	forall(n in N)
 	 (sum(h in H) works[n, h]) >= minHours*(sum(h in H) works[n, h] >= 1);
 
 /* All nurses should work, at most, maxHours hours */	
 	forall(n in N)
 	  sum(h in H) works[n, h] <= maxHours;
 	  
  /* All nurses should work, at most, maxConsec hours */
    forall(n in N)
     forall(h in H: h <= hours-maxConsec)
     	sum(index in 0..maxConsec) works[n, h+index] <= maxConsec;
    
  /* No nurse can stay at the hospital more than maxPresence hours */
 	 forall(n in N)
      forall(h in H)
        forall(h2 in H: h2 >= h+1)
          if (h2 <= hours+1-maxPresence)
          	works[n,h]+works[n,maxPresence-1+h2] <= 1;
          	
	/* No nurse can rest more than a consecutive hour */
	
	forall(n in N)
     forall(h in 2..hours)
       worksBefore[n, h] == ((sum(h2 in H: h2 < h) works[n, h2]) >= 1);
   
   forall(n in N)
     forall(h in H)
       worksAfter[n, h] == ((sum(h3 in H: h3 > h) works[n, h3]) >= 1);
      
    forall(n in N)
     forall(h in H: h <= hours-1)
       (1-works[n, h]) + worksBefore[n,h] + worksAfter[n,h] + 
       (1-works[n, h+1]) + worksBefore[n,h+1] + worksAfter[n,h+1] <= 5;
  		 
 }
 
 execute { // Should not be changed. Assumes that variables works[n][h] are used.
  	for (var n in N) {
		write("Nurse ");
		if (n < 10) write(" ");
		write(n + " works:  ");
		var minHour = -1;
		var maxHour = -1;
		var totalHours = 0;
		for (var h in H) {
		  	if (works[n][h] == 1) {
		  		totalHours++;
		  		write("  W");	
		  		if (minHour == -1) minHour = h;
		  		maxHour = h;			  	
		  	}
		  	else write("  .");
   		}
   		if (minHour != -1) write("  Presence: " + (maxHour - minHour +1));
   		else write("  Presence: 0")
   		writeln ("\t(TOTAL " + totalHours + "h)");		  		  
	}		
	writeln("");
	write("Demand:          ");
	
	for (h in H) {
	if (demand[h] < 10) write(" ");
	write(" " + demand[h]);	
	}
	writeln("");
	write("Assigned:        ");
	for (h in H) {
		var total = 0;
		for (n in N)
			if (works[n][h] == 1) total = total+1;
		if (total < 10) write(" ");
		write(" " + total);		
	}		
}  
 
