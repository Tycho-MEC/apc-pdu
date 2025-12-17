# apc-pdu
<a id="readme-top"></a>

<!-- PROJECT LOGO 
<br />
<div align="center">
  <a href="https://github.com/github_username/repo_name">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>
-->
<h3 align="center">APC PDU Control for Home Assistant</h3>

  <p align="center">
    Remote control and monitoring of APC Power Distribution Units from Home Assistant
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about">About</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#compatability">Compatability</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT -->
## About

This custom component provides an integration for Home Assistant to control APC PDUs using SNMP.

Control and monitoring of the PDUs was already possible using the built-in SNMP integration but has the limitations of needing manual configuration from the config file and each output being presented as a separate entity that couldn't be edited from the UI.  This component presents the PDU using Home Assistant's device and entity model, allowing configuration from the UI and functionality like relabelling outputs or assigning them to an area so they can be targetted by automations.



<!-- GETTING STARTED -->
## Getting Started

### Compatability

This integration was developed for the AP7920B, but it will likely work with other APC PDUs that have a simmilar MIB structure.

The integration has been tested and proven to work with the following devices:
* AP7920B
* AP7921B (thanks to [@zotanmew](zotanmew))
* AP8981 - without per port power monitoring (thanks to [@zotanmew](zotanmew))

### Installation

To install the integration:

1. Clone the repository
2. Copy the apc_pdu folder to the custom_components folder in your Home Assistant installation
3. Restart Home Assistant

Support for HACS installation is planned.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE -->
## Usage

SNMPv2 must be enabled on the PDU and be accessible from the Home Assistant installation!

To add a new matrix to Home Assistant:

1. Go to "Settings" -> "Devices & services" to open the Integrations page, and then select "Add integration".
2. If the integration has been sucessfully installed "APC PDU" will be available in the list.
3. Add the following details:
* host - the hostname or IP address of the management port of the PDU.
* community - the SNMP community configured on the PDU
4. Click submit.

The PDU will be added to Home Assistant as a device with a separate entity for each output.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

Planned features:

- [ ] HACS Integration
- [ ] PDU model identifcation
- [ ] PDU health monitoring
- [ ] Support for more APC PDU models

See the [open issues](https://github.com/Tycho-MEC/extron_mav/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. I'm not a professional dev and any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/github_username/repo_name/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=github_username/repo_name" alt="contrib.rocks image" />
</a>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgements

Thanks to:

* Home Assistant for the incredible open source platform. [https://www.home-assistant.io/](https://www.home-assistant.io/)
* The Best Readme Template. [https://github.com/othneildrew/Best-README-Template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
