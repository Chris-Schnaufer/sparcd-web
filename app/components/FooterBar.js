
/** @module components/FooterBar */

import styles from './components.module.css';

/**
 * Renders the footer bar
 * @function
 * @returns {object} The rendered footer
 */
export default function FooterBar() {
  const cur_year = new Date().getFullYear();
  const prev_year = cur_year <= 2023 ? "" : "2023-";

  return (
    <footer id='sparcd-footer' className={styles.footerbar} role="group" style={{position:'fixed', left:'0px', bottom:'0px'}}>
      <div className={styles.footer_wrapper} id="footer_details_wrapper">
        <div className={styles.footer_sub_title} aria_describedby="footer_contibutors">Contributors&nbsp;
          <span className={styles.footer_more_info}>&#x00BB;</span>
        </div>
        <div className={`${styles.footer_details_wrapper} ${styles.footer_details_left}`} role="tooltip" id="footer_contibutors">
          <div className={styles.footer_sub_item}>UA Computer Science <span className={styles.outside_link}>&#x2197;</span></div>
          <div className={styles.footer_sub_item}>UA Communications & Cyber Technologies Data Science <span className={styles.outside_link}>&#x2197;</span></div>
          <div className={styles.footer_sub_item}>UA Wildcat Research and Conservation Center <span className={styles.outside_link}>&#x2197;</span></div>
          <div className={styles.footer_sub_item}>School of Natural Resources and the Environment <span className={styles.outside_link}>&#x2197;</span></div>
        </div>
      </div>
      <div className={styles.footer_copyright}>Copyright &copy; {prev_year}{cur_year}</div>
      <div className={styles.footer_wrapper} style={{justifyContent: 'center'}}>
        <div className={styles.footer_sub_title} aria_describedby="footer_credits">Credits&nbsp;
          <span className={styles.footer_more_info}>&#x00BB;</span>
        </div>
        <div className={`${styles.footer_details_wrapper} ${styles.footer_details_right}`} role="tooltip" id="footer_credits">
          <div className={styles.footer_sub_item} id="footer_sub_item">Dr. Melanie Culver <span className={styles.outside_link}>&#x2197;</span></div>
          <div className={styles.footer_sub_item}>Susan Malusa <span className={styles.outside_link}>&#x2197;</span></div>
          <div className={styles.footer_sub_item}>David Slovilosky <span className={styles.outside_link}>&#x2197;</span></div>
          <div className={styles.footer_sub_item}>Julian Pistorus <span className={styles.outside_link}>&#x2197;</span></div>
          <div className={styles.footer_sub_item}>Chris Schnaufer <span className={styles.outside_link}>&#x2197;</span></div>
        </div>
      </div>
    </footer>
  );
}