#!/usr/bin/perl -w


# ----------------------------------------------------------------------
use LWP::UserAgent;
use LWP::ConnCache;
use Data::Dumper;
use JSON::XS;
use File::Copy;
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
my $CONTENT_DIR		= '/home/alessio/Wiji/demos/kivy-cinema-kiosk/content/movies/';
my $VIDEOS_DIR		= '/home/alessio/Wiji/demos/kivy-cinema-kiosk/content/movies.old/trailers.tmp/';
# ----------------------------------------------------------------------





########################################################################

my $index_file	= shift or die 'no movie index file';

my $index		= read_movies_index_file($index_file);

my $agent		= create_agent();

foreach my $movie (@$index) {
	print $movie->{id}."\n";

	my $html_page		= download($movie->{url}) or die 'cannot download given URL';
	
	my $movie_info		= extract_movie_info($movie, $html_page);
	my $show_times		= create_random_show_times(14, 2);
	my $related_movies	= pick_random_related_movies($movie, $index);

	my $json			= JSON::XS->new->pretty(1)->encode({
		%$movie_info,
		show_times		=> $show_times,
		related			=> $related_movies
	});
	
	my $background_img	= download_background_picture($movie->{url});

	save_movie_data($movie, $background_img, $json);

}


########################################################################





# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub save_movie_data {
	my ($movie, $background, $data) = @_;

	my $movie_data_path	= $CONTENT_DIR.$movie->{id};
	my $trailer_video	= $VIDEOS_DIR.$movie->{video};

	mkdir($movie_data_path);
	
	copy($trailer_video, $movie_data_path.'/trailer.avi');
	
	write_to_disk($data, $movie_data_path.'/data.json');
	write_to_disk($background, $movie_data_path.'/poster.jpg');
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub write_to_disk {
	my ($data, $file) = @_;
	
	open(OUT, '>', $file); binmode(OUT);
	print OUT $data;
	close(OUT);
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub read_movies_index_file {
	my ($filename) = @_;
	
	my @index;
	open(IN, $filename);
	while (my $t = readline(IN)) {chomp($t);
		my ($apple_url, $video_name) = split(/\t+/, $t);
			next unless $apple_url && $video_name;
		
		my $id = get_movie_id($apple_url);
		
		push @index, {
			id		=> $id,
			url		=> $apple_url,
			video	=> $video_name
		};
		
	}
	close(IN);
	
	return \@index;
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub pick_random_related_movies {
	my ($current_movie_id, $movies_index) = @_;
	
	my @filtered = sort {rand() <=> rand()} grep {$current_movie_id ne $_} map {$_->{id}} @$movies_index;
	
	return [@filtered[0..2]];
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub create_agent {
	return new LWP::UserAgent(
		agent		=> 'Firefox/3.0',
		timeout		=> 5,
		conn_cache	=> new LWP::ConnCache()
	);
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub download {
	my ($url) = @_;
	
	my $response = $agent->get($url);
	
	return $response->content() if $response->is_success();
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub extract_movie_info {
	my ($movie, $html) = @_;
	
	return {
		id			=> $movie->{id},
		title		=> get_title($html),
		summary		=> get_summary($html),
		rating		=> get_rating($html),
		genre		=> get_genre($html),
		site		=> get_official_site($html),
		director	=> get_director($html),
		cast		=> get_cast($html)
	}
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub clean {
	my ($text) = @_;
	
	$text =~ s/<.+?>/ /g;
	$text =~ s/\s+/ /gs;
	$text =~ s/^\s+|\s+$//g;
	$text =~ s/(\w)\s+(\W)/$1$2/g;
	
	return $text;
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub get_movie_id {
	my ($url) = @_;
	return $1 if $url =~ /([^\/]+)\/$/;
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub get_summary {
	my ($html) = @_;
	return clean($1) if $html =~ /<div id="more-description" class="read-more-container">.+?<p>(.+?)<\/p>/s;
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub get_rating {
	my ($html) = @_;
	return clean($1) if $html =~ /<img class="rating (.+?)"/;
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub get_genre {
	my ($html) = @_;
	return clean($1) if $html =~ /<dt>Genre:<\/dt>(.+?)<\/dd>/;
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub get_official_site {
	my ($html) = @_;
	return $1 if $html =~ /<a class="official-link" href="(.+?)"/;
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub get_director {
	my ($html) = @_;
	return clean($1) if $html =~ /<dt>Director:<\/dt><dd>(.+?)<\/dd>/;
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub get_title {
	my ($html) = @_;
	return clean($1) if $html =~ /<h1 class="replaced">(.+?)<\/h1>/;
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub get_cast {
	my ($html) = @_;
	my $cast_str = clean($1) if $html =~ /<dt>Cast:<\/dt><dd>(.+?)<\/dd>/;
	return [split(/\s*,\s*/, $cast_str)];
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub create_random_show_times {
	my ($n_theatres, $n_shows) = @_;
	
	my @theatres = sort {rand() <=> rand()} (1..$n_theatres);
	
	my @shows;
	for (1..$n_shows) {
		my $theatre_id = pop(@theatres);
		my $direction	= ($theatre_id > ($n_theatres/2) ? 'left' : 'right');
		
		my $hour = int(rand(12)+10);
		my $ampm = ($hour > 12 ? 'pm' : 'am');
		
		push @shows, {
			direction	=> $direction,
			theatre		=> $theatre_id,
			time		=> ($hour%12).$ampm
		};
	}
	
	return \@shows;
}
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
sub download_background_picture {
	my ($movie_url) = @_;
	
	return download($movie_url.'images/background.jpg');
}
# ----------------------------------------------------------------------
