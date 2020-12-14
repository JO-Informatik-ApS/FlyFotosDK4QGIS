# FlyFotosDK4QGIS

FlyFotosDK - Samling af Danmarks historiske flyfotos, plugin til QGIS

Tjenesten FlyFotosDK udbyder mere end 1.200 unikke historiske flyfotoserier, svarende til godt en halv million individuelle billeder. Det store billede katalog dækker Danmark i flere årtier og skalaer. Læs mere om løsningen på <a href="https://flyfotos.dk/">https://flyfotos.dk/</a>

Denne plugin gør det nemt at overskue de mange flyfotoserier. Du kan f.eks. vælge at få en oversigt over de ”synlige” serier i kortvinduet. Derudover kan du udvælge serier via skala eller fra et givet årti.

For at kunne anvende denne plugin skal du have etableret en brugerkonto til tjenesten - Læs mere her:

<a href="https://flyfotos.dk/da-dk/produkter/adgang">https://flyfotos.dk/da-dk/produkter/adgang</a>

English:

The FlyFotosDK service offers more than 1.200 unique historical aerial photoseries, which is the equivalent of more than half a million individual photos. This large catalogue covers the whole of Denmark, divided over multiple decades and several scales. Read more about the service on the website <a href="https://flyfotos.dk/">https://flyfotos.dk/</a>

This plugin helps with managing the many aerial photoseries. It allows you for example to get an overview of the visible layers in the current map canvas extent. Alternately you can sort the photoseries based on scale for a given decade.

To use this plugin you need to have you need to have an account - read more here <a href="https://flyfotos.dk/da-dk/produkter/adgang">https://flyfotos.dk/da-dk/produkter/adgang</a>

   <img src="https://flyfotos.dk/Portals/2/flyfotodk-logo.png?ver=2020-05-20-124201-440" alt="FlyfotosDK" width="201" height="62">

## Introduction

This project is for a QGIS companion plugin to the website <a href="https://flyfotos.dk/">https://flyfotos.dk/</a>. The plugin let's the user see the layers that they have access to inside QGIS, add layers to their current project, and find layers that overlap the current extent of the user's viewport (and add these to their current project).

## Compatibility

The plugin is compatible with QGIS versions 3.4 and above.

## Releases

You can find the latest release as a zip file on [QGIS plugin website](https://plugins.qgis.org/plugins/) or over in [the release section](https://github.com/JO-Informatik-ApS/FlyFotosDK4QGIS/releases), where you can download them and give them a try.

## Issues

If you have any problems or difficulties running the client, feel free to [create a new issue here](https://github.com/JO-Informatik-ApS/FlyFotosDK4QGIS/issues "Create an issue").

## Known issues

Layers are not being loaded. Failure to load appears as error in QGIS Log messages window as:

"WARNING Map request failed `[error: Error transferring {link here}]`

We have found this error on QGIS versions 3.10.0 - 3.10.1.

**A fix** for this error is to update QGIS to a later version (either latest LTR, or the latest live).

## Authors

- **Nisha Vijai**
- **Valdas Zabulionis**

Developed at **JO Informatik ApS**  
Website: [**https://jo-informatik.dk/**](https://jo-informatik.dk/)

## License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.
