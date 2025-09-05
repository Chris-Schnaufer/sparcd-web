package model.util;

import model.constant.SanimalMetadataFields;
import model.location.Location;
import model.species.SpeciesEntry;
import model.util.MetadataUtils;

import javafx.beans.property.SimpleObjectProperty;
import javafx.collections.ObservableList;

import org.apache.commons.imaging.ImageReadException;
import org.apache.commons.imaging.ImageWriteException;
import org.apache.commons.imaging.formats.tiff.constants.TiffDirectoryType;
import org.apache.commons.imaging.formats.tiff.taginfos.TagInfoAscii;
import org.apache.commons.imaging.formats.tiff.taginfos.TagInfoShort;
import org.apache.commons.imaging.formats.tiff.TiffImageMetadata;
import org.apache.commons.imaging.formats.tiff.constants.ExifTagConstants;
import org.apache.commons.imaging.formats.tiff.write.TiffOutputDirectory;
import org.apache.commons.imaging.formats.tiff.write.TiffOutputSet;
import org.apache.commons.lang.exception.ExceptionUtils;

import java.io.File;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * Class containing utils for writing & reading metadata
 */
public class UpdateExif
{
	private static final DateTimeFormatter DATE_FORMAT_FOR_DISK = DateTimeFormatter.ofPattern("yyyy:MM:dd HH:mm:ss");

	/**
	 * Writes the species and location tagged in this image to the disk
	 * 
	 * @param file
	 *            The file (must be an image file)
	 */
	public static void writeToDisk(File file, List<SpeciesEntry> speciesPresent, Location location)
	{
		if (speciesPresent == null && location == null)
			return;

		try
		{
			// Read the output set from the image entry
			TiffOutputSet outputSet = MetadataUtils.readOutputSet(file);

			// Grab the EXIF directory from the output set
			TiffOutputDirectory exif = outputSet.getOrCreateExifDirectory();
			exif.removeField(ExifTagConstants.EXIF_TAG_DATE_TIME_ORIGINAL);
			exif.add(ExifTagConstants.EXIF_TAG_DATE_TIME_ORIGINAL, DATE_FORMAT_FOR_DISK.format(LocalDateTime.now()));

			// Grab the sanimal directory from the output set
			TiffOutputDirectory directory = MetadataUtils.getOrCreateSanimalDirectory(outputSet);

			if (speciesPresent != null)
			{
				// Remove the species field if it exists
				directory.removeField(SanimalMetadataFields.SPECIES_ENTRY);
				// Use the species format name, scientific name, count
				String[] metaVals = speciesPresent.stream().map(speciesEntry -> speciesEntry.getSpecies().getName() + ", " + speciesEntry.getSpecies().getScientificName() + ", " + speciesEntry.getAmount()).toArray(String[]::new);
				// Add the species entry field
				directory.add(SanimalMetadataFields.SPECIES_ENTRY, metaVals);
			}

			// If we have a valid location, write that too
			if (location != null)
			{
				// Write the lat/lng
				outputSet.setGPSInDegrees(location.getLng(), location.getLat());
				// Remove the location entry name and elevation
				directory.removeField(SanimalMetadataFields.LOCATION_ENTRY);
				// Add the new location entry name and elevation
				directory.add(SanimalMetadataFields.LOCATION_ENTRY, location.getName(), location.getElevation().toString(), location.getId());
			}

			Integer exceptionCount = 0;
			Boolean writeDone = false;
			Exception caughtException = null;

			while (writeDone == false)
			{
				try
				{
					// Write the metadata
					MetadataUtils.writeOutputSet(outputSet, file);
					writeDone = true;
				}
				catch (IOException | ImageWriteException e)
				{
					exceptionCount++;
					try
					{
						Thread.sleep(1000);
					}
					catch(InterruptedException ex)
					{
					}
					
					if (exceptionCount >= 3)
					{
						writeDone = true;
						caughtException = e;
					}
				}
			}
			if (caughtException != null)
			{
				if (caughtException instanceof IOException)
				{ 
					throw (IOException)caughtException;
				} else {
					throw (ImageWriteException)caughtException;
				}
			}
		}
		catch (ImageReadException | IOException | ImageWriteException e)
		{
			System.out.println("Error writing metadata to the image " + file.getName() + "!\n" + ExceptionUtils.getStackTrace(e));
			System.exit(1);
		}
	}
}
