# Databases Description

The MWA image plane transients app uses a PostgreSQL database with the following tables (which Django refers to as models).
These models are defined in `gleam_webapp/candidate_app/models.py`.

For a more detailed ERD see [this image](figures/DB_ERD.svg).

## Observation

Fields defined:

- observation_id (required, primary key)
- obsname
- starttime
- stoptime
- ra_tile_dec
- dec_tile_dec
- ra_tile_hms
- dec_tile_dms
- projectid
- azimuth
- elevation
- frequency_channels
- cent_freq
- freq_res
- int_time

## Project

Fields defined:

- id (required, primary key)
- name (must be unique)
- description

## Filter

Fields defined:

- id (required, primary key)
- name (must be unique)
- description

## Classification

Fields defined:

- id (required, primary key)
- name (must be unique)
- description

## Candidate

Fields defined:

- id (required, primary key)
- obs_id (references observation.observation_id)
- filter (references filter.id)
- project (references project.id)
- png_path
- gif_path
- notes
- x_pix
- y_pix
- ra_deg
- dec_deg
- cent_sep_deg
- rad_pix
- rad_deg
- area_pix
- can_peak_flux
- can_fluence
- can_beam
- can_det_stat
- can_mod_ind
- nks_name
- nks_x_pix
- nks_y_pix
- nks_ra_deg
- nks_dec_deg
- nks_flux
- nks_res
- nks_res_dif
- nks_det_stat
- nks_sep_pix
- nks_sep_deg
- can_nks_flux_rat
- can_nks_is_close
- ra_hms
- dec_dms
- nks_ra_hms
- nks_dec_dms

## Metadata

- candidate (references candidate)
- text

## Rating:

Fields defined:

- id (required, primary key)
- candidate (references candidate)
- user (references user in auth db)
- rating
- classification (references classification)
- date

## ATNFPulsar

Fields defined:

- id (required, primary key)
- name (unique)
- decj (required)
- raj (required)
- DM
- p0
- s400

## Association

- candidate (references candidate, primary_key)
- pulsar (references pulsar)
