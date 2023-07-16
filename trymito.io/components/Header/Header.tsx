import Image from "next/image"
import Link from "next/link"
import { useState } from "react"

import headerStyles from './Header.module.css'
import CloseButton from '../../public/CloseButton.png'
import TranslucentButton from "../TranslucentButton/TranslucentButton"
import GithubButton, { MITO_GITHUB_LINK } from "../GithubButton/GithubButton"
import { classNames } from "../../utils/classNames"

export const MITO_INSTALLATION_DOCS_LINK = 'https://docs.trymito.io/getting-started/installing-mito'
export const JOBS_BOARD_LINK = 'https://www.ycombinator.com/companies/mito/jobs'

const Header = (): JSX.Element => {

    const [mobileMenuVisible, setMobileMenuVisible] = useState(false)

    return (
        <header className={headerStyles.header}>
          <div className={headerStyles.desktop_left_nav_bar}>
            <Link href='/'>
              <a> {/* We have to add this for the link to work, see here: https://github.com/vercel/next.js/issues/20434 */}
                <Image src="/Mito.svg" alt="Mito Logo" width={50} height={30}/>
              </a>
            </Link>
            <nav className={classNames(headerStyles.desktop_menu_items, 'display-desktop-only-flex')}>
              <ul className={classNames(headerStyles.nav_item)}>
                <li className={classNames('highlight-on-hover', headerStyles.dropdown_container)}>
                  <span>Product </span>
                  <div className={headerStyles.dropdown_anchor_container}>
                    <Image src={'/down-anchor.svg'} alt='Dropdown indicator' width={16} height={6} />
                  </div>
                  <ul className={headerStyles.dropdown}>
                    <li>
                      <Link href='/spreadsheet-automation'>
                        <div className={classNames(headerStyles.dropdown_item)}>
                          <div className={classNames(headerStyles.dropdown_item_row)}>
                            <Image src={'/step-icons/spreadsheet_icon.svg'} alt='Mito spreadsheet' width={20} height={20} />
                            <p className='margin-top-0'> 
                              Mito Spreadsheet 
                            </p>
                          </div>
                          <div className={classNames(headerStyles.dropdown_item_row)}>
                            <p className={headerStyles.dropdown_item_subtext}>
                              Edit a spreadsheet. Generate Python code.
                            </p>
                          </div>   
                        </div>
                      </Link>                 
                    </li>

                    <li>
                      <Link href='/python-ai-tools'>
                        <div className={classNames(headerStyles.dropdown_item)}>
                          <div className={classNames(headerStyles.dropdown_item_row)}>
                            <Image src={'/step-icons/ai_icon.svg'} alt='Mito AI' width={20} height={20} />
                            <p className='margin-top-0'>
                              Mito AI
                            </p>
                          </div>
                          <div className={classNames(headerStyles.dropdown_item_row)}>
                            <p className={headerStyles.dropdown_item_subtext}>
                              Automate your report with a Python expert.
                            </p>
                          </div>
                        </div>
                      </Link>
                    </li>

                    <li>
                      <Link href='/infrastructure-integration-python-tool'>
                        <div className={classNames(headerStyles.dropdown_item)}>
                          <div className={classNames(headerStyles.dropdown_item_row)}>
                            <Image src={'/step-icons/SettingsIconThin.svg'} alt='Customize Mito' width={20} height={20} />
                            <p className='margin-top-0'>
                              Custom Functionality
                            </p>
                          </div>
                          <div className={classNames(headerStyles.dropdown_item_row)}>
                            <p className={headerStyles.dropdown_item_subtext}>
                              BYO spreadsheet functions and imports methods.
                            </p>
                          </div>
                        </div>
                      </Link>
                    </li>



                  </ul>
                </li>
                <li className={classNames('highlight-on-hover', headerStyles.nav_item)}>
                  <Link href='/plans'>Plans</Link>
                </li>
                <li className={classNames('highlight-on-hover', headerStyles.nav_item)}>
                  <Link href='/security'>Security</Link>
                </li>
                <li className={classNames('highlight-on-hover', headerStyles.nav_item)}>
                  <Link href='https://blog.trymito.io'>Blog</Link>
                </li>
                <li className={classNames('highlight-on-hover', headerStyles.nav_item)}>
                  <a href='https://docs.trymito.io' target="_blank" rel="noreferrer">Docs</a>
                </li>
              </ul>
            </nav>
          </div>

          <div className={headerStyles.desktop_right_nav_bar}>
              <GithubButton 
                variant='Star'
                text='Github'
              />              
              <TranslucentButton
                href={MITO_INSTALLATION_DOCS_LINK}
              >
                <>
                  Install
                </>
              </TranslucentButton>
          </div>


          {/* This next section is the header for mobile only */}
          <div 
            className={classNames(headerStyles.menu_bar_container, 'display-mobile-only')}
            aria-controls='mobile_nav_menu'
            onClick={() => setMobileMenuVisible(mobileMenuVisible => !mobileMenuVisible)}
          >
            {/* Menu adapted from: https://www.w3schools.com/howto/tryit.asp?filename=tryhow_css_menu_icon_js */}
            <div className={headerStyles.menu_bar}></div>
            <div className={headerStyles.menu_bar}></div>
            <div className={headerStyles.menu_bar}></div>
          </div>
          <div 
            id='mobile_nav_menu' 
            className={classNames(headerStyles.mobile_nav_menu, {[headerStyles.mobile_nav_menu_hidden]: !mobileMenuVisible})}
          >
            <div className={headerStyles.mobile_nav_bar_close_container}>
              <div className={headerStyles.mobile_nav_bar_close_button}
                onClick={() => setMobileMenuVisible(false)}
              >
                <Image src={CloseButton} alt='close mobile navbar' width={30} height={30} />
              </div>
            </div>
            <nav>
              <ul>
                <li className='highlight-on-hover'>
                  <Link href='/spreadsheet-automation'>Mito Spreadsheet</Link>
                </li>
                <li className='highlight-on-hover'>
                  <Link href='/python-ai-tools'>Mito AI</Link>
                </li>
                <li className='highlight-on-hover'>
                  <Link href='/infrastructure-integration-python-tool'>Custom Functionality</Link>
                </li>
                <li className='highlight-on-hover'>
                  <Link href='/plans'>Plans</Link>
                </li>
                <li className='highlight-on-hover'>
                  <Link href='/security'>Security</Link>
                </li>
                <li className='highlight-on-hover'>
                  <Link href='https://blog.trymito.io'>Blog</Link>
                </li>
                <li className='highlight-on-hover'>
                  <a href='https://docs.trymito.io' target="_blank" rel="noreferrer">Docs</a>
                </li>
                <li className='highlight-on-hover'>
                  <a href={MITO_GITHUB_LINK} target="_blank" rel="noreferrer">GitHub</a>
                </li>
                <li className='highlight-on-hover'>
                  <a href={JOBS_BOARD_LINK} target="_blank" rel="noreferrer">We&apos;re hiring!</a>
                </li>
              </ul>
            </nav>
          </div>
        </header>
    )
}

export default Header;