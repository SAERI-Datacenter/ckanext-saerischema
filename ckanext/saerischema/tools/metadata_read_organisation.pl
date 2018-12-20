#!/usr/bin/env perl

use Text::CSV;
open($fh, "metadata_FK_export181112_new.csv") || die "cannot open csv";
my $csv = Text::CSV->new ({ binary => 1, auto_diag => 1 });
$csv->column_names ($csv->getline ($fh)); # use header
while (my $row = $csv->getline_hr ($fh)) {
	printf "%s\n", $row->{organisation};
	#OR $raw->[0] etc
}
close $fh;

