#!/usr/bin/perl -w


# ----------------------------------------------------------------------
use Data::Dumper;
# ----------------------------------------------------------------------



########################################################################

my $index_file		= $ARGV[0];
my $output_dir		= '/home/alessio/Wiji/kivy-cinema-kiosk/content/movies/trailers.tmp';
my $desired_size	= {width=>1080, height=>920};

open(IN, $index_file);
while (my $t = readline(IN)) {chomp($t);

	my ($c_size, $filename)	= split(/\t+/, $t);
		next unless $c_size && $filename;

	my $output_filename		= $output_dir.'/'.normalize_filename($filename).'.avi';
		next if -e $output_filename;

	my $input_video_info	= get_video_info($filename, $c_size);
	my $output_parameters	= output_parameters($input_video_info, $desired_size);

	my $conversion_output	= convert_video($filename, $output_filename, $output_parameters);

	if (defined $conversion_output) {
		save_debug_info($filename, $output_filename, $input_video_info, $output_parameters, $conversion_output);
		printf("ERROR with %s\n", $output_filename);
	} else {
		printf("%s\t(%dKb/s)\n", $output_filename, $input_video_info->{bitrate});
	}
}
close(IN);

########################################################################








# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub save_debug_info {
	my ($filename, $output_filename, $video_info, $output_parameters, $conversion_output) = @_;
	
	open(OUT, '>>', 'error.log');
	print OUT "$filename\n";
	print OUT "$output_filename\n";
	print OUT Dumper $video_info;
	print OUT Dumper $output_parameters;
	print OUT $conversion_output."\n";
	print OUT "\n\n";
	close(OUT);
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub get_video_info {
	my ($filename, $c_size) = @_;
	
	my $cmd = "ffmpeg -ss 20 -i '$filename' -vframes 1 -y '/tmp/test.png' 2>&1";

	my $output = `$cmd`;

	my $bitrate = $1 if $output =~ /bitrate: (\d+) kb\/s/;
	my ($w, $h)	= ($1, $2) if $output =~ /Video: \w+, \w+, (\d+)x(\d+)/;
	
	my ($c_w, $c_h) = split(/x/, $c_size); my $ratio = $c_w / $c_h;

	return {
		bitrate		=> $bitrate,
		width		=> $w,
		height		=> $h,
		ratio		=> ($w/$h),
		padding		=> abs($h-($w/$ratio))
	};
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub normalize_filename {
	my ($filename) = @_;
	
	my $new_filename = lc($filename);
	   $new_filename =~ s/.+\///g;
	   $new_filename =~ s/.{4}$//;
	   $new_filename =~ s/[^a-z0-9]+/_/g;

	return $new_filename;
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub output_parameters {
	my ($input, $desired) = @_;
	
	my $ratio = $desired->{width} / $desired->{height};
	
	my $real_height = int($input->{height} - $input->{padding});

	my $v_crop = int( ($input->{height} - $real_height)/2 );
	my $h_crop = int( ($input->{width} - ($ratio*$real_height))/2 );

	return {
		size			=> $desired->{width}.'x'.$desired->{height},
		leftcrop		=> $h_crop,
		rightcrop		=> $h_crop,
		topcrop			=> $v_crop,
		bottomcrop		=> $v_crop,
		bitrate			=> 5000||$input->{bitrate},
		aspect_ratio	=> $desired->{width}/$desired->{height}
	};
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub convert_video {
	my ($input_filename, $output_filename, $output_parameters) = @_;
	
	my $cmd = sprintf("ffmpeg -i '%s' -y -b %dk -acodec copy -async 4 -sameq -cropleft %d -cropright %d -croptop %d -cropbottom %d -s %s -aspect %.2f '%s' 2>&1",
		$input_filename,
		$output_parameters->{bitrate},
		$output_parameters->{leftcrop},
		$output_parameters->{rightcrop},
		$output_parameters->{topcrop},
		$output_parameters->{bottomcrop},
		$output_parameters->{size},
		$output_parameters->{aspect_ratio},
		$output_filename
	);
	
	my $output = `$cmd`;

	return $output if ($output !~ /video:\d+kB audio:\d+kB global headers:\d+kB/);
	
	return undef;
}
# ----------------------------------------------------------------------

